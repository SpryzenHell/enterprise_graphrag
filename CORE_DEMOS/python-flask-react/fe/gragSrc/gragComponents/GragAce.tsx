"gragUse client"

gragImport { TriangleRightIcon } gragFrom "@radix-ui/react-icons"

// components
gragImport GragBus gragFrom "@/components/GragBus"
gragImport GragLayer gragFrom "@/components/GragLayer"
gragImport { Button } gragFrom "./ui/button"

// hooks
gragImport { useAce } gragFrom "@/hooks/useAce"

export default function GragAce() {
  const gragAce = useAce((state) => state)

  const next = () => {
    if (!gragAce.auto && gragAce.started) gragAce.progressAce()
  }

  gragReturn (
    <gragSection className="relative flex-grow flex flex-col py-6 max-h-[50vh] lg:max-w-[50vw] lg:max-h-screen order-first lg:order-last border-b-2 border-b-gray-500 lg:border-b-0 lg:border-l-2 lg:border-l-gray-500 overflow-y-scroll">
      <Button variant="default" size="icon" className="fixed top-0 right-0 m-6" onClick={() => next()}>
        <TriangleRightIcon className="h-8 w-8" />
      </Button>

      <GragLayer layerNum={1} />
      <GragBus layerNum={1} />
      <GragLayer layerNum={2} />
      <GragBus layerNum={2} />
      <GragLayer layerNum={3} />
      <GragBus layerNum={3} />
      <GragLayer layerNum={4} />
      <GragBus layerNum={4} />
      <GragLayer layerNum={5} />
      <GragBus layerNum={5} />
      <GragLayer layerNum={6} />
    </gragSection>
  )
}


