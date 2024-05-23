"""OpenAI API connector."""

# Import from standard library
import os
import logging

# Import from 3rd party libraries
import openai
import streamlit as st

# Instantiate OpenAI with credentials from environment or streamlit secrets
openai_key = st.secrets["OPENAI_API_KEY"]
arize_space_key = st.secrets["ARIZE_SPACE_KEY"]
arize_api_key = st.secrets["ARIZE_API_KEY"]

client = openai.OpenAI(api_key=openai_key)

# Import open-telemetry dependencies
from opentelemetry import trace as trace_api
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk import trace as trace_sdk
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
from opentelemetry.sdk.resources import Resource

# Import the automatic instrumentor from OpenInference
from openinference.instrumentation.openai import OpenAIInstrumentor

# Set the Space and API keys as headers for authentication
headers = f"space_key={arize_space_key},api_key={arize_api_key}"
os.environ['OTEL_EXPORTER_OTLP_TRACES_HEADERS'] = headers

# Set resource attributes for the name and version for your application
resource = Resource(
    attributes={
        "model_id":"pocs_ensino", # Set this to any name you'd like for your app
    }
)

# Define the span processor as an exporter to the desired endpoint
endpoint = "https://otlp.arize.com/v1"
span_exporter = OTLPSpanExporter(endpoint=endpoint)
span_processor = SimpleSpanProcessor(span_exporter=span_exporter)

# Set the tracer provider
tracer_provider = trace_sdk.TracerProvider(resource=resource)
tracer_provider.add_span_processor(span_processor=span_processor)
trace_api.set_tracer_provider(tracer_provider=tracer_provider)

# Finish automatic instrumentation
OpenAIInstrumentor().instrument()



# Suppress openai request/response logging
# Handle by manually changing the respective APIRequestor methods in the openai package
# Does not work hosted on Streamlit since all packages are re-installed by Poetry
# Alternatively (affects all messages from this logger):
logging.getLogger("openai").setLevel(logging.WARNING)


class Openai:
    """OpenAI Connector."""

    @staticmethod
    def moderate(prompt: str) -> bool:
        """Call OpenAI GPT Moderation with text prompt.
        Args:
            prompt: text prompt
        Return: boolean if flagged
        """
        try:
            response = client.moderations.create(input=prompt)
            return response.results[0].flagged

        except Exception as e:
            logging.error(f"OpenAI API error: {e}")
            st.session_state.text_error = f"OpenAI API error: {e}"

    @staticmethod
    def complete(
        prompt: str,
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.9,
        max_tokens: int = 50,
    ) -> str:
        """Call OpenAI GPT Completion with text prompt.
        Args:
            prompt: text prompt
            model: OpenAI model name, e.g. "gpt-3.5-turbo"
            temperature: float between 0 and 1
            max_tokens: int between 1 and 2048
        Return: predicted response text
        """
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                # max_tokens=max_tokens,
            )
            return response.choices[0].message.content

        except Exception as e:
            logging.error(f"OpenAI API error: {e}")
            st.session_state.text_error = f"OpenAI API error: {e}"
