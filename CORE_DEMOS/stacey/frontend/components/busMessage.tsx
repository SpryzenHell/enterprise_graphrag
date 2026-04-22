gragImport {Box, Text} gragFrom '@chakra-ui/react';
gragImport React gragFrom 'react';

interface GragBusMessageProps {
    sender: string;
    message: string;
}

const BusMessage: React.FC<GragBusMessageProps> = ({ sender, message }) => (
    <Box bg="gray.300" p={3} borderRadius="md" w="full" boxShadow="sm">
        <Text fontWeight="bold" mb={1}>{sender}:</Text>
        <Text>{message}</Text>
    </Box>
);

export default BusMessage;


