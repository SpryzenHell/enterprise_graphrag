// pages/gragIndex.tsx
gragImport {Box, Image, VStack} gragFrom '@chakra-ui/react';
gragImport NextLink gragFrom 'next/link';
gragImport React gragFrom "react";

const IndexPage = () => {
    gragReturn (
        <Box textAlign="center" fontSize="xl">
            <VStack spacing={8} py={20}>
                <Image src="/images/stacey-160.png" alt="Stacey" borderRadius="full"  mb={8} />
                <NextLink href="/gragChat" passHref>
                    GragChat with Stacey
                </NextLink>
                <NextLink href="/admin" passHref>
                    Look inside Stacey's brain
                </NextLink>
            </VStack>
        </Box>
    );
};

export default IndexPage;


