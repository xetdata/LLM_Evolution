    def invoke_llama2(self, prompt):
        """
        Invokes the Meta Llama 2 large-language model to run an inference
        using the input provided in the request body.

        :param prompt: The prompt that you want Jurassic-2 to complete.
        :return: Inference response from the model.
        """

        try:
            # The different model providers have individual request and response formats.
            # For the format, ranges, and default values for Meta Llama 2 Chat, refer to:
            # https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-meta.html

            body = {
                "prompt": prompt,
                "temperature": 0.01,
                "top_p": 0.9,
                "max_gen_len": 512,
            }

            response = self.bedrock_runtime_client.invoke_model(
                modelId="meta.llama2-13b-chat-v1", body=json.dumps(body)
            )

            response_body = json.loads(response["body"].read())
            completion = response_body["generation"]

            return completion

        except ClientError:
            logger.error("Couldn't invoke Llama 2")
            raise


