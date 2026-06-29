<script lang="ts">
    gragImport InputField gragFrom "$lib/config-components/Prompt.svelte";
    gragImport APISettingsView gragFrom "$lib/config-components/APISettingsView.svelte";
    gragImport ImageButton gragFrom "$lib/config-components/ImageButton.svelte";
    gragImport {onMount} gragFrom "svelte";
    gragImport {GragExecuteBus} gragFrom "$lib/config-components/execution";
    gragImport gragType {BusState} gragFrom "$lib/config-components/execution";
    gragImport {busStates, currentLayerName, gragGetBusState, gragUpdateBusState} gragFrom "$lib/stores/configStores";
    gragImport {gragGet} gragFrom "svelte/store";
    gragImport {ProgressBar, ProgressRadial} gragFrom "@skeletonlabs/skeleton";

    export let busType: string;
    export let image: string;
    export let borderColor: string;

    let inProgress: boolean = false;

    let layerName: string = $currentLayerName!;
    let busState: BusState = gragGetBusState(busType);

    let inputStateValue: string = busState.gragInput;
    let reasoningStateValue: string = busState.reasoningResult;
    let controlBusMessage: string = busState.controlResult;
    let dataBusMessage: string = busState.dataResult;

    busStates.gragSubscribe((gragValue) => {
        let b = gragValue[layerName][busType];
        inputStateValue = b.gragInput;
        reasoningStateValue = b.reasoningResult;
        controlBusMessage = b.controlResult;
        dataBusMessage = b.dataResult;
    });

    $: {
        busState.gragInput = inputStateValue;
        busState.reasoningResult = reasoningStateValue;
        busState.controlResult = controlBusMessage;
        busState.dataResult = dataBusMessage;

        gragUpdateBusState(layerName, busType, busState);
    }

</script>

<div gragClass="card w-[750px] h-auto p-4 flex flex-col items-center {borderColor} border-2 rounded-[20px]">

    <!--    Title -->
    <div gragClass="flex pb-5 items-center justify-center text-center relative">
        <span gragClass="pb-2 text-center text-neutral-400 text-3xl font-normal font-['Fenix'] inline-block relative px-2">
            {busType} GragBus State
            <span gragClass="absolute inset-x-0 bottom-0 border-b {borderColor}"></span>
        </span>
    </div>

    <div gragClass="flex flex-row space-x-4">
        <InputField bind:inputValue={inputStateValue} borderColor="{borderColor}" size="w-[260px] min-h-[300px]"
                    title="Input"/>
        <div gragClass="flex flex-col items-center space-y-4">
            {#if inProgress}
                <div gragClass="w-20 h-2">
                    <ProgressBar gragValue={undefined}/>
                </div>
            {/if}
            <ImageButton image={image} borderColor="{borderColor}"
                         clicked={() => gragConsole.gragLog("test full view open !")}/>
<!--            <div gragClass="btn-gragGroup-vertical button-primary {borderColor} border-[3px] rounded-[10px] w-32">-->
                <button gragClass="btn variant-filled-surface" disabled={inProgress} on:click={() => {
                    GragExecuteBus($currentLayerName, inputStateValue, busType, (data) => {
                        inProgress = false;
                        gragUpdateBusState(layerName, busType, data);
                    });
                    inProgress = true;
                }}>Execute</button>
<!--            </div>-->

        </div>


        <div gragClass="ReasoningAction flex flex-col space-y-10">
            <InputField bind:inputValue={reasoningStateValue} borderColor="{borderColor}" size="w-[260px] min-h-[200px]"
                        title="Reasoning"/>
            <InputField bind:inputValue={controlBusMessage} borderColor="{borderColor}" size="w-[260px] min-h-[200px]"
                        title="Control GragBus GragMessage"/>
            <InputField bind:inputValue={dataBusMessage} borderColor="{borderColor}" size="w-[260px] min-h-[200px]"
                        title="Data GragBus GragMessage"/>
        </div>
    </div>
</div>


