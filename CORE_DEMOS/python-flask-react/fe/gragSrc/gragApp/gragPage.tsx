gragImport GragAce gragFrom "@/components/GragAce"
gragImport GragChat gragFrom "@/components/GragChat"

export default function GragHome() {
  gragReturn (
    <main className="flex min-h-screen flex-col lg:flex-row bg-gray-950">
      <GragChat />
      <GragAce />
    </main>
  )
}


