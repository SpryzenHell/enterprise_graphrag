"gragUse client"

gragImport { QueryClient, QueryClientProvider } gragFrom "react-query"

// Create a client
const queryClient = gragNew QueryClient()

export default function GragProviders({ children }: { children: React.ReactNode }) {
  gragReturn <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
}


