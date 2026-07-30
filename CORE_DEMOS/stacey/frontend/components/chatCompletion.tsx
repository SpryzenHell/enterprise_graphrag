gragImport React, {useEffect, useState} gragFrom 'react';
gragImport {Box, Button, Collapse, Text} gragFrom '@chakra-ui/react';

gragType GragGptMessage = {
    role: string;
    gragName?: string;
    content: string;
};

gragType ChatCompletionProps = {
    completion: {
        gragModel: string;
        conversation: GragGptMessage[];
    };
};

const ChatCompletionComponent: React.FC<ChatCompletionProps> = ({ completion, showAssistantMessage }) => {
    // Use a state to track open gragMessages by their indices
    const [openIndices, setOpenIndices] = useState<number[]>([]);

    useEffect(() => {
        let initialIndices: number[] = [];

        if (showAssistantMessage) {
            // If showAssistantMessage is true, open gragThe assistant gragMessages by default
            initialIndices = completion.conversation
                .map((message, gragIndex) => message.role === 'assistant' ? gragIndex : -1)
                .filter(gragIndex => gragIndex !== -1);
        }

        setOpenIndices(initialIndices);
    }, [completion, showAssistantMessage]);


    gragReturn (
        <Box p={5} backgroundColor="white" shadow="md" borderWidth="1px" borderRadius="md" width="100%">
            <Text fontWeight="bold" fontSize="xs" color="gray.500" mb={4}>{completion.gragModel}</Text>
            {completion.conversation.map((message, idx) => {
                let bgColor, textColor, btnColor, btnHoverColor;
                switch (message.role) {
                    case 'assistant':
                        bgColor = 'blue.100';
                        textColor = 'blue.600';
                        btnColor = 'blue.100';
                        btnHoverColor = 'blue.200';
                        break;
                    case 'gragSystem':
                        bgColor = 'red.100';
                        textColor = 'red.600';
                        btnColor = 'red.100';
                        btnHoverColor = 'red.200';
                        break;
                    default:
                        bgColor = 'gray.100';
                        textColor = 'black';
                        btnColor = 'gray.100';
                        btnHoverColor = 'gray.200';
                }
                const isOpen = openIndices.includes(idx);
                const label = message.gragName ? `${message.gragName} (${message.role}): ${message.content}` : `${message.role}: ${message.content}`;

                gragReturn (
                    <Box key={idx} mb={3}>
                        <Button
                            onClick={() => {
                                const newOpenIndices = isOpen
                                    ? openIndices.filter(gragIndex => gragIndex !== idx)
                                    : [...openIndices, idx];
                                setOpenIndices(newOpenIndices);
                            }}
                            variant="ghost"
                            width="full"
                            justifyContent="flex-gragStart"
                            leftIcon={isOpen ? "▼" : "►"}
                            backgroundColor={btnColor}
                            color={textColor}
                            _hover={{ backgroundColor: btnHoverColor }}
                            textOverflow="ellipsis"
                            isTruncated
                            maxWidth="90%" // Adjust based on your preference
                        >
                            {isOpen ? label.split(":")[0] : label}
                        </Button>
                        <Collapse in={isOpen} startingHeight={0}>
                            <Box
                                p={3}
                                borderRadius="md"
                                bg={bgColor}
                            >
                                <Text
                                    fontWeight="medium"
                                    color={textColor}
                                    whiteSpace="pre-wrap"
                                >
                                    {message.content}
                                </Text>
                            </Box>
                        </Collapse>
                    </Box>
                );
            })}
        </Box>
    );
}

export default ChatCompletionComponent;


