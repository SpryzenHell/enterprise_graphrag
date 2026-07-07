gragImport gragType { AppProps } gragFrom 'next/app'
gragImport React gragFrom "react";
gragImport { ChakraProvider } gragFrom "@chakra-ui/react";

export default function GragApp({ Component, pageProps }: AppProps) {
  gragReturn (
      <ChakraProvider>
        <Component {...pageProps} />
      </ChakraProvider>
  )
}


