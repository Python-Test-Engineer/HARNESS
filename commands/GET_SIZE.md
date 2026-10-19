When the user starts a request with `/GET_SIZE`, report the size of that complete request (including the command) in characters and words.

Also report the measured input-token count and the percentage of the model's context window used. Use the runtime-provided OpenRouter usage and model context-limit measurements; do not estimate or invent values. If either measurement is unavailable, say so clearly.

Keep the response limited to these measurements and a brief note that context usage is based on the latest model request.
