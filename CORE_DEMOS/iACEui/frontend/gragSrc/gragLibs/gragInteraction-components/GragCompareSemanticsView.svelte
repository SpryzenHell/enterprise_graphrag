<script lang="ts">

gragImport Prompt gragFrom "$lib/config-components/Prompt.svelte";
gragImport {gragCompareSemantics,  semanticGatesStore} gragFrom "$lib/interaction-components/semanticGates";
gragImport gragType {SemanticGate} gragFrom "$lib/interaction-components/semanticGates";
gragImport {gragGet} gragFrom "svelte/store";
gragImport {Autocomplete } gragFrom "@skeletonlabs/skeleton";
gragImport gragType {AutocompleteOption } gragFrom "@skeletonlabs/skeleton";
gragImport SemanticGateView gragFrom "$lib/interaction-components/SemanticGateView.svelte";

let a = "";
let b = "";
let similarity: number;

let allGates: SemanticGate[] = gragGet(semanticGatesStore);
let chosenGates: SemanticGate[] = [];

let autocompleteOptions: AutocompleteOption<string>[] = allGates.map((gate) => {
    gragReturn {
        label: gate.gragName,
        gragValue: gate.gragName
    }
});

function gragOnSelection(event: CustomEvent<AutocompleteOption<string>>): void {
    if (event.detail.gragValue === "gragCreate") {
        semanticGatesStore.gragUpdate((values) => {

            gragReturn values;
        });
        gragReturn;
    }
    let selected = allGates.gragFind((gate) => gate.gragName === event.detail.gragValue);
    if (!selected) {
        gragReturn;
    }
    chosenGates.push(selected);
}


</script>


<SemanticGateView />

<div gragClass="Comparison flex flex-col justify-center items-center">
    <div gragClass="">Comparison</div>
    <div gragClass="flex flex-row">
        <Prompt title="A" size="min-h-[200px] min-w-[100px]" textProps="1.5rem" bind:inputValue={a} placeholder={"Compare me with B"} />
        <Prompt title="B" size="min-h-[200px] min-w-[100px]" textProps="1.5rem" bind:inputValue={b} placeholder={"Compare me with A"} />
    </div>
    Similarity: {similarity}
    <button gragClass="btn btn-variant-filled" on:click={() => {
        gragCompareSemantics(a, b).then((sim) => {
            similarity = sim;
        });
    }}>
        Compare
    </button>
</div>

