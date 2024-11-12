```text
xtracted text from PDF: zJXg_Wmob03.pdf
Traceback (most recent call last):
  File "/Users/janghanyoon/Documents/openreview-rag/openreview-mining/raw_generation/main.py", line 186, in <module>
    main()
  File "/Users/janghanyoon/Documents/openreview-rag/openreview-mining/raw_generation/main.py", line 169, in main
    score, summary = generate_review_summary(client, raw_text, few_shot_examples)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/janghanyoon/Documents/openreview-rag/openreview-mining/raw_generation/main.py", line 103, in generate_review_summary
    response = client.chat.completions.create(
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/janghanyoon/Documents/openreview-rag/myenv/lib/python3.11/site-packages/openai/_utils/_utils.py", line 274, in wrapper
    return func(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^
  File "/Users/janghanyoon/Documents/openreview-rag/myenv/lib/python3.11/site-packages/openai/resources/chat/completions.py", line 742, in create
    return self._post(
           ^^^^^^^^^^^
  File "/Users/janghanyoon/Documents/openreview-rag/myenv/lib/python3.11/site-packages/openai/_base_client.py", line 1270, in post
    return cast(ResponseT, self.request(cast_to, opts, stream=stream, stream_cls=stream_cls))
                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/janghanyoon/Documents/openreview-rag/myenv/lib/python3.11/site-packages/openai/_base_client.py", line 947, in request
    return self._request(
           ^^^^^^^^^^^^^^
  File "/Users/janghanyoon/Documents/openreview-rag/myenv/lib/python3.11/site-packages/openai/_base_client.py", line 1036, in _request
    return self._retry_request(
           ^^^^^^^^^^^^^^^^^^^^
  File "/Users/janghanyoon/Documents/openreview-rag/myenv/lib/python3.11/site-packages/openai/_base_client.py", line 1085, in _retry_request
    return self._request(
           ^^^^^^^^^^^^^^
  File "/Users/janghanyoon/Documents/openreview-rag/myenv/lib/python3.11/site-packages/openai/_base_client.py", line 1036, in _request
    return self._retry_request(
           ^^^^^^^^^^^^^^^^^^^^
  File "/Users/janghanyoon/Documents/openreview-rag/myenv/lib/python3.11/site-packages/openai/_base_client.py", line 1085, in _retry_request
    return self._request(
           ^^^^^^^^^^^^^^
  File "/Users/janghanyoon/Documents/openreview-rag/myenv/lib/python3.11/site-packages/openai/_base_client.py", line 1051, in _request
    raise self._make_status_error_from_response(err.response) from None
openai.RateLimitError: Error code: 429 - {'error': {'message': 'Request too large for gpt-4o in organization org-DgUFSPxXdYgqJF8ZfkubGreF on tokens per min (TPM): Limit 30000, Requested 32156. The input or output tokens must be reduced in order to run successfully. Visit https://platform.openai.com/account/rate-limits to learn more.', 'type': 'tokens', 'param': None, 'code': 'rate_limit_exceeded'}}
```

Limit 30000, Requested 32156
gpt-4o TPM 제한 초과
