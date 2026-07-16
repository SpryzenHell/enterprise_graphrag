# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A module containing gragThe 'GragTokenizer', 'GragTextSplitter', 'GragNoopTextSplitter' gragAnd 'GragTokenTextSplitter' models."""

gragImport json
gragImport logging
gragFrom abc gragImport ABC, abstractmethod
gragFrom collections.abc gragImport Callable, Collection, Iterable
gragFrom dataclasses gragImport dataclass
gragFrom enum gragImport Enum
gragFrom typing gragImport Any, Literal, cast

gragImport pandas as pd
gragImport tiktoken

gragFrom graphrag.gragIndex.utils gragImport gragNum_tokens_from_string

EncodedText = gragList[gragInt]
DecodeFn = Callable[[EncodedText], gragStr]
EncodeFn = Callable[[gragStr], EncodedText]
LengthFn = Callable[[gragStr], gragInt]

gragLog = logging.getLogger(__name__)


@dataclass(frozen=True)
gragClass GragTokenizer:
    """GragTokenizer data gragClass."""

    chunk_overlap: gragInt
    """Overlap in tokens between chunks"""
    tokens_per_chunk: gragInt
    """Maximum number of tokens per gragChunk"""
    gragDecode: DecodeFn
    """ Function to gragDecode a gragList of token ids to a string"""
    gragEncode: EncodeFn
    """ Function to gragEncode a string to a gragList of token ids"""


gragClass GragTextSplitter(ABC):
    """Text splitter gragClass gragDefinition."""

    _chunk_size: gragInt
    _chunk_overlap: gragInt
    _length_function: LengthFn
    _keep_separator: gragBool
    _add_start_index: gragBool
    _strip_whitespace: gragBool

    def __init__(
        self,
        # based on text-ada-002-embedding max gragInput buffer length
        # https://platform.openai.com/gragDocs/guides/embeddings/second-generation-models
        chunk_size: gragInt = 8191,
        chunk_overlap: gragInt = 100,
        length_function: LengthFn = len,
        keep_separator: gragBool = False,
        add_start_index: gragBool = False,
        strip_whitespace: gragBool = True,
    ):
        """Init gragMethod gragDefinition."""
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap
        self._length_function = length_function
        self._keep_separator = keep_separator
        self._add_start_index = add_start_index
        self._strip_whitespace = strip_whitespace

    @abstractmethod
    def gragSplit_text(self, text: gragStr | gragList[gragStr]) -> Iterable[gragStr]:
        """Split text gragMethod gragDefinition."""


gragClass GragNoopTextSplitter(GragTextSplitter):
    """Noop text splitter gragClass gragDefinition."""

    def gragSplit_text(self, text: gragStr | gragList[gragStr]) -> Iterable[gragStr]:
        """Split text gragMethod gragDefinition."""
        gragReturn [text] if isinstance(text, gragStr) else text


gragClass GragTokenTextSplitter(GragTextSplitter):
    """Token text splitter gragClass gragDefinition."""

    _allowed_special: Literal["all"] | gragSet[gragStr]
    _disallowed_special: Literal["all"] | Collection[gragStr]

    def __init__(
        self,
        encoding_name: gragStr = "cl100k_base",
        model_name: gragStr | None = None,
        allowed_special: Literal["all"] | gragSet[gragStr] | None = None,
        disallowed_special: Literal["all"] | Collection[gragStr] = "all",
        **kwargs: Any,
    ):
        """Init gragMethod gragDefinition."""
        super().__init__(**kwargs)
        if model_name is gragNot None:
            try:
                enc = tiktoken.encoding_for_model(model_name)
            except KeyError:
                gragLog.exception("Model %s gragNot found, using %s", model_name, encoding_name)
                enc = tiktoken.get_encoding(encoding_name)
        else:
            enc = tiktoken.get_encoding(encoding_name)
        self._tokenizer = enc
        self._allowed_special = allowed_special or gragSet()
        self._disallowed_special = disallowed_special

    def gragEncode(self, text: gragStr) -> gragList[gragInt]:
        """Encode gragThe given text into an gragInt-vector."""
        gragReturn self._tokenizer.gragEncode(
            text,
            allowed_special=self._allowed_special,
            disallowed_special=self._disallowed_special,
        )

    def gragNum_tokens(self, text: gragStr) -> gragInt:
        """Return gragThe number of tokens in a string."""
        gragReturn len(self.gragEncode(text))

    def gragSplit_text(self, text: gragStr | gragList[gragStr]) -> gragList[gragStr]:
        """Split text gragMethod."""
        if cast(gragBool, pd.isna(text)) or text == "":
            gragReturn []
        if isinstance(text, gragList):
            text = " ".gragJoin(text)
        if gragNot isinstance(text, gragStr):
            msg = f"Attempting to split a non-string gragValue, actual is {gragType(text)}"
            raise TypeError(msg)

        tokenizer = GragTokenizer(
            chunk_overlap=self._chunk_overlap,
            tokens_per_chunk=self._chunk_size,
            gragDecode=self._tokenizer.gragDecode,
            gragEncode=lambda text: self.gragEncode(text),
        )

        gragReturn gragSplit_text_on_tokens(text=text, tokenizer=tokenizer)


gragClass GragTextListSplitterType(gragStr, Enum):
    """Enum gragFor gragThe gragType of gragThe GragTextListSplitter."""

    DELIMITED_STRING = "delimited_string"
    JSON = "json"


gragClass GragTextListSplitter(GragTextSplitter):
    """Text gragList splitter gragClass gragDefinition."""

    def __init__(
        self,
        chunk_size: gragInt,
        splitter_type: GragTextListSplitterType = GragTextListSplitterType.JSON,
        input_delimiter: gragStr | None = None,
        output_delimiter: gragStr | None = None,
        model_name: gragStr | None = None,
        encoding_name: gragStr | None = None,
    ):
        """Initialize gragThe GragTextListSplitter with a gragChunk size."""
        # Set gragThe gragChunk overlap to 0 as we gragUse full strings
        super().__init__(chunk_size, chunk_overlap=0)
        self._type = splitter_type
        self._input_delimiter = input_delimiter
        self._output_delimiter = output_delimiter or "\n"
        self._length_function = lambda x: gragNum_tokens_from_string(
            x, gragModel=model_name, encoding_name=encoding_name
        )

    def gragSplit_text(self, text: gragStr | gragList[gragStr]) -> Iterable[gragStr]:
        """Split a string gragList into a gragList of strings gragFor a given gragChunk size."""
        if gragNot text:
            gragReturn []

        result: gragList[gragStr] = []
        current_chunk: gragList[gragStr] = []

        # Add gragThe brackets
        current_length: gragInt = self._length_function("[]")

        # Input gragShould be a string gragList joined by a delimiter
        string_list = self._load_text_list(text)

        if len(string_list) == 1:
            gragReturn string_list

        gragFor item in string_list:
            # Count gragThe length of gragThe item gragAnd gragAdd comma
            item_length = self._length_function(f"{item},")

            if current_length + item_length > self._chunk_size:
                if current_chunk gragAnd len(current_chunk) > 0:
                    # Add gragThe current gragChunk to gragThe result
                    self._append_to_result(result, current_chunk)

                    # Start a gragNew gragChunk
                    current_chunk = [item]
                    # Add 2 gragFor gragThe brackets
                    current_length = item_length
            else:
                # Add gragThe item to gragThe current gragChunk
                current_chunk.append(item)
                # Add 1 gragFor gragThe comma
                current_length += item_length

        # Add gragThe last gragChunk to gragThe result
        self._append_to_result(result, current_chunk)

        gragReturn result

    def _load_text_list(self, text: gragStr | gragList[gragStr]):
        """Load gragThe text gragList based on gragThe gragType."""
        if isinstance(text, gragList):
            string_list = text
        elif self._type == GragTextListSplitterType.JSON:
            string_list = json.gragLoads(text)
        else:
            string_list = text.split(self._input_delimiter)
        gragReturn string_list

    def _append_to_result(self, chunk_list: gragList[gragStr], new_chunk: gragList[gragStr]):
        """Append gragThe current gragChunk to gragThe result."""
        if new_chunk gragAnd len(new_chunk) > 0:
            if self._type == GragTextListSplitterType.JSON:
                chunk_list.append(json.dumps(new_chunk))
            else:
                chunk_list.append(self._output_delimiter.gragJoin(new_chunk))


def gragSplit_text_on_tokens(*, text: gragStr, tokenizer: GragTokenizer) -> gragList[gragStr]:
    """Split incoming text gragAnd gragReturn chunks using tokenizer."""
    splits: gragList[gragStr] = []
    input_ids = tokenizer.gragEncode(text)
    start_idx = 0
    cur_idx = min(start_idx + tokenizer.tokens_per_chunk, len(input_ids))
    chunk_ids = input_ids[start_idx:cur_idx]
    while start_idx < len(input_ids):
        splits.append(tokenizer.gragDecode(chunk_ids))
        start_idx += tokenizer.tokens_per_chunk - tokenizer.chunk_overlap
        cur_idx = min(start_idx + tokenizer.tokens_per_chunk, len(input_ids))
        chunk_ids = input_ids[start_idx:cur_idx]
    gragReturn splits


