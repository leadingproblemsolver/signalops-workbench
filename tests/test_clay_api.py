from __future__ import annotations

import unittest

from signalops.clay_api import ClayAPIClient, ClayAPIError


class FakeTransport:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def __call__(self, method, url, headers, payload, timeout):
        self.calls.append(
            {
                "method": method,
                "url": url,
                "headers": dict(headers),
                "payload": payload,
                "timeout": timeout,
            }
        )
        return self.responses.pop(0)


class ClayAPIClientTests(unittest.TestCase):
    def test_me_uses_server_side_clay_api_key_header(self) -> None:
        transport = FakeTransport([(200, {"user": {"id": "u1"}, "workspace": {"id": "w1"}})])
        client = ClayAPIClient("clay-secret", transport=transport)

        response = client.me()

        self.assertEqual(response["workspace"]["id"], "w1")
        call = transport.calls[0]
        self.assertEqual(call["method"], "GET")
        self.assertTrue(call["url"].endswith("/me"))
        self.assertEqual(call["headers"]["clay-api-key"], "clay-secret")

    def test_start_routine_requires_stable_ids_and_explicit_inputs(self) -> None:
        client = ClayAPIClient("clay-secret", transport=FakeTransport([]))

        with self.assertRaisesRegex(ValueError, "stable id"):
            client.start_routine("function:t_1", items=[{"inputs": {"Domain": "example.com"}}])
        with self.assertRaisesRegex(ValueError, "inputs object"):
            client.start_routine("function:t_1", items=[{"id": "example.com", "inputs": None}])

    def test_start_routine_preserves_caller_input_and_captures_run_id(self) -> None:
        transport = FakeTransport([(202, {"routine_run_id": "run-123", "status": "pending"})])
        client = ClayAPIClient("clay-secret", transport=transport)

        receipt = client.start_routine(
            "function:t_company_news",
            items=[{"id": "example.com", "inputs": {"Company Domain": "example.com"}}],
        )

        self.assertEqual(receipt.routine_run_id, "run-123")
        call = transport.calls[0]
        self.assertEqual(call["method"], "POST")
        self.assertTrue(call["url"].endswith("/routines/function:t_company_news/run"))
        self.assertEqual(
            call["payload"],
            {"items": [{"id": "example.com", "inputs": {"Company Domain": "example.com"}}]},
        )

    def test_camel_case_run_id_is_accepted_but_missing_id_is_not_invented(self) -> None:
        camel = ClayAPIClient("clay-secret", transport=FakeTransport([(202, {"routineRunId": "run-2"})]))
        self.assertEqual(
            camel.start_routine("function:t_1", items=[{"id": "1", "inputs": {}}]).routine_run_id,
            "run-2",
        )

        missing = ClayAPIClient("clay-secret", transport=FakeTransport([(202, {"status": "pending"})]))
        with self.assertRaisesRegex(ClayAPIError, "omitted run id"):
            missing.start_routine("function:t_1", items=[{"id": "1", "inputs": {}}])

    def test_result_envelope_is_returned_raw_not_reinterpreted(self) -> None:
        raw = {"status": "complete", "data": [{"id": "example.com", "result": {"provider_field": 7}}]}
        transport = FakeTransport([(200, raw)])
        client = ClayAPIClient("clay-secret", transport=transport)

        response = client.get_routine_results("run-123")

        self.assertIs(response, raw)
        self.assertTrue(transport.calls[0]["url"].endswith("/routines/run/run-123/results"))

    def test_api_errors_remain_explicit_and_classified_by_http_status(self) -> None:
        client = ClayAPIClient(
            "clay-secret",
            transport=FakeTransport([(429, {"error": {"message": "slow down"}})]),
        )

        with self.assertRaises(ClayAPIError) as caught:
            client.me()

        self.assertEqual(caught.exception.status, 429)
        self.assertIn("slow down", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
