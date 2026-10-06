# Support bot (Driftfix demo)

A small customer-support bot built on the **OpenAI Assistants API**: threads, polled runs, and a
function tool that looks up order status.

OpenAI shut the Assistants API down on **August 26, 2026**. This repo deliberately still uses it
(and pins `openai==1.40.0`) so [Driftfix](https://github.com/sjanney/driftfix) can show how it
migrates real code to the Responses and Conversations APIs: it opens a pull request with the fix,
upgrades the SDK, and reports the test results.

```sh
pip install -r requirements.txt
pytest
```
