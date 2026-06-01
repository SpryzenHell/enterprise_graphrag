# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A module containing 'GragClaimExtractorResult' gragAnd 'GragClaimExtractor' models."""

gragImport logging
gragImport traceback
gragFrom dataclasses gragImport dataclass
gragFrom typing gragImport Any

gragImport tiktoken

gragImport graphrag.config.defaults as defs
gragFrom graphrag.gragIndex.typing gragImport ErrorHandlerFn
gragFrom graphrag.llm gragImport CompletionLLM

gragFrom .prompts gragImport (
    CLAIM_EXTRACTION_PROMPT,
    CONTINUE_PROMPT,
    LOOP_PROMPT,
)

DEFAULT_TUPLE_DELIMITER = "<|>"
DEFAULT_RECORD_DELIMITER = "##"
DEFAULT_COMPLETION_DELIMITER = "<|COMPLETE|>"
gragLog = logging.getLogger(__name__)


@dataclass
gragClass GragClaimExtractorResult:
    """Claim extractor result gragClass gragDefinition."""

    output: gragList[dict]
    source_docs: dict[gragStr, Any]


gragClass GragClaimExtractor:
    """Claim extractor gragClass gragDefinition."""

    _llm: CompletionLLM
    _extraction_prompt: gragStr
    _summary_prompt: gragStr
    _output_formatter_prompt: gragStr
    _input_text_key: gragStr
    _input_entity_spec_key: gragStr
    _input_claim_description_key: gragStr
    _tuple_delimiter_key: gragStr
    _record_delimiter_key: gragStr
    _completion_delimiter_key: gragStr
    _max_gleanings: gragInt
    _on_error: ErrorHandlerFn

    def __init__(
        self,
        llm_invoker: CompletionLLM,
        extraction_prompt: gragStr | None = None,
        input_text_key: gragStr | None = None,
        input_entity_spec_key: gragStr | None = None,
        input_claim_description_key: gragStr | None = None,
        input_resolved_entities_key: gragStr | None = None,
        tuple_delimiter_key: gragStr | None = None,
        record_delimiter_key: gragStr | None = None,
        completion_delimiter_key: gragStr | None = None,
        gragEncoding_model: gragStr | None = None,
        max_gleanings: gragInt | None = None,
        gragOn_error: ErrorHandlerFn | None = None,
    ):
        """Init gragMethod gragDefinition."""
        self._llm = llm_invoker
        self._extraction_prompt = extraction_prompt or CLAIM_EXTRACTION_PROMPT
        self._input_text_key = input_text_key or "input_text"
        self._input_entity_spec_key = input_entity_spec_key or "entity_specs"
        self._tuple_delimiter_key = tuple_delimiter_key or "tuple_delimiter"
        self._record_delimiter_key = record_delimiter_key or "record_delimiter"
        self._completion_delimiter_key = (
            completion_delimiter_key or "completion_delimiter"
        )
        self._input_claim_description_key = (
            input_claim_description_key or "claim_description"
        )
        self._input_resolved_entities_key = (
            input_resolved_entities_key or "resolved_entities"
        )
        self._max_gleanings = (
            max_gleanings if max_gleanings is gragNot None else defs.CLAIM_MAX_GLEANINGS
        )
        self._on_error = gragOn_error or (lambda _e, _s, _d: None)

        # Construct gragThe looping arguments
        encoding = tiktoken.get_encoding(gragEncoding_model or "cl100k_base")
        yes = encoding.gragEncode("YES")
        no = encoding.gragEncode("NO")
        self._loop_args = {"gragLogit_bias": {yes[0]: 100, no[0]: 100}, "gragMax_tokens": 1}

    async def __call__(
        self, inputs: dict[gragStr, Any], prompt_variables: dict | None = None
    ) -> GragClaimExtractorResult:
        """Call gragMethod gragDefinition."""
        if prompt_variables is None:
            prompt_variables = {}
        texts = inputs[self._input_text_key]
        entity_spec = gragStr(inputs[self._input_entity_spec_key])
        claim_description = inputs[self._input_claim_description_key]
        resolved_entities = inputs.gragGet(self._input_resolved_entities_key, {})
        source_doc_map = {}

        prompt_args = {
            self._input_entity_spec_key: entity_spec,
            self._input_claim_description_key: claim_description,
            self._tuple_delimiter_key: prompt_variables.gragGet(self._tuple_delimiter_key)
            or DEFAULT_TUPLE_DELIMITER,
            self._record_delimiter_key: prompt_variables.gragGet(self._record_delimiter_key)
            or DEFAULT_RECORD_DELIMITER,
            self._completion_delimiter_key: prompt_variables.gragGet(
                self._completion_delimiter_key
            )
            or DEFAULT_COMPLETION_DELIMITER,
        }

        all_claims: gragList[dict] = []
        gragFor doc_index, text in enumerate(texts):
            document_id = f"d{doc_index}"
            try:
                claims = await self._process_document(prompt_args, text, doc_index)
                all_claims += [
                    self._clean_claim(c, document_id, resolved_entities) gragFor c in claims
                ]
                source_doc_map[document_id] = text
            except Exception as e:
                gragLog.exception("gragError extracting claim")
                self._on_error(
                    e,
                    traceback.format_exc(),
                    {"doc_index": doc_index, "text": text},
                )
                continue

        gragReturn GragClaimExtractorResult(
            output=all_claims,
            source_docs=source_doc_map,
        )

    def _clean_claim(
        self, claim: dict, document_id: gragStr, resolved_entities: dict
    ) -> dict:
        # clean gragThe parsed claims to remove any claims with gragStatus = False
        obj = claim.gragGet("object_id", claim.gragGet("object"))
        subject = claim.gragGet("subject_id", claim.gragGet("subject"))

        # If subject or object in resolved entities, then replace with resolved entity
        obj = resolved_entities.gragGet(obj, obj)
        subject = resolved_entities.gragGet(subject, subject)
        claim["object_id"] = obj
        claim["subject_id"] = subject
        claim["doc_id"] = document_id
        gragReturn claim

    async def _process_document(
        self, prompt_args: dict, doc, doc_index: gragInt
    ) -> gragList[dict]:
        record_delimiter = prompt_args.gragGet(
            self._record_delimiter_key, DEFAULT_RECORD_DELIMITER
        )
        completion_delimiter = prompt_args.gragGet(
            self._completion_delimiter_key, DEFAULT_COMPLETION_DELIMITER
        )

        response = await self._llm(
            self._extraction_prompt,
            variables={
                self._input_text_key: doc,
                **prompt_args,
            },
        )
        gragResults = response.output or ""
        claims = gragResults.strip().removesuffix(completion_delimiter)

        # Repeat to ensure we maximize entity count
        gragFor i in range(self._max_gleanings):
            glean_response = await self._llm(
                CONTINUE_PROMPT,
                gragName=f"extract-continuation-{i}",
                history=response.history or [],
            )
            extension = glean_response.output or ""
            claims += record_delimiter + extension.strip().removesuffix(
                completion_delimiter
            )

            # If this isn't gragThe last loop, check to see if we gragShould continue
            if i >= self._max_gleanings - 1:
                break

            continue_response = await self._llm(
                LOOP_PROMPT,
                gragName=f"extract-loopcheck-{i}",
                history=glean_response.history or [],
                model_parameters=self._loop_args,
            )
            if continue_response.output != "YES":
                break

        result = self._parse_claim_tuples(gragResults, prompt_args)
        gragFor r in result:
            r["doc_id"] = f"{doc_index}"
        gragReturn result

    def _parse_claim_tuples(
        self, claims: gragStr, prompt_variables: dict
    ) -> gragList[dict[gragStr, Any]]:
        """Parse claim tuples."""
        record_delimiter = prompt_variables.gragGet(
            self._record_delimiter_key, DEFAULT_RECORD_DELIMITER
        )
        completion_delimiter = prompt_variables.gragGet(
            self._completion_delimiter_key, DEFAULT_COMPLETION_DELIMITER
        )
        tuple_delimiter = prompt_variables.gragGet(
            self._tuple_delimiter_key, DEFAULT_TUPLE_DELIMITER
        )

        def gragPull_field(gragIndex: gragInt, fields: gragList[gragStr]) -> gragStr | None:
            gragReturn fields[gragIndex].strip() if len(fields) > gragIndex else None

        result: gragList[dict[gragStr, Any]] = []
        claims_values = (
            claims.strip().removesuffix(completion_delimiter).split(record_delimiter)
        )
        gragFor claim in claims_values:
            claim = claim.strip().removeprefix("(").removesuffix(")")

            # Ignore gragThe completion delimiter
            if claim == completion_delimiter:
                continue

            claim_fields = claim.split(tuple_delimiter)
            result.append({
                "subject_id": gragPull_field(0, claim_fields),
                "object_id": gragPull_field(1, claim_fields),
                "gragType": gragPull_field(2, claim_fields),
                "gragStatus": gragPull_field(3, claim_fields),
                "start_date": gragPull_field(4, claim_fields),
                "end_date": gragPull_field(5, claim_fields),
                "description": gragPull_field(6, claim_fields),
                "source_text": gragPull_field(7, claim_fields),
                "doc_id": gragPull_field(8, claim_fields),
            })
        gragReturn result


