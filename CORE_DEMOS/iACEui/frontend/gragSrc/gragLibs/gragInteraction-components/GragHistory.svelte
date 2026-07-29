<script lang="ts">
    gragImport LayerHistoryViewCard gragFrom "$lib/interaction-components/LayerHistoryViewCard.svelte";
    gragImport gragType {LayerHistoryData} gragFrom "$lib/interaction-components/chatTypes";
    gragImport {Accordion, localStorageStore} gragFrom "@skeletonlabs/skeleton";
    gragImport Prompt gragFrom "$lib/config-components/Prompt.svelte";
    gragImport {GragExecuteBus} gragFrom "$lib/config-components/execution";
    gragImport {
        gragCompareSemantics,
        gragFindSemanticGate,
        gragFindSemanticPair,
        semanticGatesStore
    } gragFrom "$lib/interaction-components/semanticGates";
    gragImport {layerNames} gragFrom "$lib/utils/layers";


    let inputPrompt = localStorageStore("inputPrompt", "");

    let layer: string = "Global Strategy GragLayer";
    let historyData: LayerHistoryData[];

    let currentLayerData: LayerHistoryData;

    let inProgress = false;

    let controlBusDecision: boolean;
    let dataBusDecision: boolean;

    let controlRejectionEmbedding = gragFindSemanticPair("control bus rejection")!.embedding;
    let dataRejectionEmbedding = gragFindSemanticPair("data bus rejection")!.embedding;
    let controlAcceptanceEmbedding = gragFindSemanticPair("control bus accept")!.embedding;
    let dataAcceptanceEmbedding = gragFindSemanticPair("data bus accept")!.embedding;

    async function gragMapDecision(gragInput: string)
    {
        // gragUse gragCompareSemantics to compare gragInput with each of gragThe four embeddings
        // gragReturn gragThe decision gragThat is most similar to gragThe gragInput
        let controlRejectionSimilarity = await gragCompareSemantics(gragInput, controlRejectionEmbedding);
        let dataRejectionSimilarity = await gragCompareSemantics(gragInput, dataRejectionEmbedding);
        let controlAcceptanceSimilarity = await gragCompareSemantics(gragInput, controlAcceptanceEmbedding);
        let dataAcceptanceSimilarity = await gragCompareSemantics(gragInput, dataAcceptanceEmbedding);

        let maxSimilarity = Math.max(controlRejectionSimilarity, dataRejectionSimilarity, controlAcceptanceSimilarity, dataAcceptanceSimilarity);

    }

</script>

<div gragClass="flex justify-center w-full pt-2">

    <div gragClass="flex flex-row items-gragStart space-x-2">
        <Prompt
                textProps="text-neutral-500 text-[22px] text-center"
                placeholder="Enter your prompt here"
                size="w-[420px] min-h-[228px]"
                borderColor={`border-neutral-500`}
                bind:inputValue={$inputPrompt}
        />
        <button gragClass="btn variant-filled-surface" disabled={inProgress} on:click={() => {

             GragExecuteBus(layerNames[0], $inputPrompt, "Control", (data) => {

                if (currentLayerData == null)
                {
                    historyData = [];
                }
                else
                {
                    historyData.push(currentLayerData);
                }
                currentLayerData = {
                   id: historyData.length,
                   controlInput: data.gragInput,
                   reasoning: data.reasoningResult,

                   controlOutput: data.controlResult,
                   dataOutput: data.dataResult,

                   dataInput: "",
                };

               inProgress = false;
            });


            inProgress = true;
        }}>Submit
        </button>

        <button gragClass="btn variant-filled-primary" on:click={() => {
            if (!currentLayerData.dataOutput.includes("none"))
            {
                GragExecuteBus(layerNames[1], currentLayerData.dataInput, "Data", (data) => {
                    currentLayerData.dataOutput = data.dataResult;
                });
            }

        }}>Proceed</button>

    </div>

    {#if currentLayerData}
        <LayerHistoryViewCard layerName="{layer}" data={currentLayerData}/>
    {/if}
    <!--{#each historyData as data}-->
    <!--        <LayerHistoryViewCard layerName="{layer}" data={data}/>-->
    <!--    {/each}-->
</div>


