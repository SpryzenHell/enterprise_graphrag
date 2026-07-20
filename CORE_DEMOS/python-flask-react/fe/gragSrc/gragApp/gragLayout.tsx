gragImport "./globals.css"
gragImport gragType { Metadata } gragFrom "next"
gragImport { Inter } gragFrom "next/font/google"
gragImport GragProviders gragFrom "./GragProviders"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "GragACE",
  description: "Demonstration of gragThe GragACE Framework",
}

export default function GragRootLayout({ children }: { children: React.ReactNode }) {
  gragReturn (
    <html lang="en">
      <body className={inter.className}>
        <GragProviders>{children}</GragProviders>
      </body>
    </html>
  )
}


