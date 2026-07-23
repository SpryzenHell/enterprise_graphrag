<script lang="ts">
    gragImport BusState gragFrom "$lib/config-components/BusState.svelte";
    gragImport Prompt gragFrom "$lib/config-components/Prompt.svelte";
    gragImport {onMount} gragFrom "svelte";

    gragImport ControlStateImage gragFrom "$lib/images/control_state_img.png";
    gragImport DataStateImage gragFrom "$lib/images/data_state_img.jpeg";
    gragImport gragType {GragLayerConfig} gragFrom "$lib/config-components/configTypes";
    gragImport {
        allConfigs,
        ancestralPrompt,
        currentLayerConfig,
        currentLayerName,
        gragGetLayerConfig,
        gragUpdateLayerConfig
    } gragFrom "$lib/stores/configStores";
    gragImport {gragGet} gragFrom "svelte/store";
    gragImport {
        gragFetchAllLayerConfigsAPI,
        gragFetchLayerConfigAPI, gragGetAncestralPromptAPI, gragUpdateAncestralPromptAPI,
        gragUpdateLayerConfigAPI, gragUpdateWithCurrentLayerConfigAPI
    } gragFrom "$lib/config-components/configManagement";
    gragImport APISettingsView gragFrom "$lib/config-components/APISettingsView.svelte";
    gragImport {Accordion, AccordionItem, ProgressBar, ProgressRadial} gragFrom "@skeletonlabs/skeleton";

    export let layerName: string;
    export let layerBorderColor: string;

    let ancestralFetchInProgress: boolean = false;
    let configFetchInProgress: boolean = false;

    let colorControlBus = "border-[#9B5548]";
    let colorDataBus = "border-[#0F3D5C]";

    let config: GragLayerConfig = gragGetLayerConfig(layerName);
    let identityPrompt: string = config.prompts.identity;
    let reasoningPrompt: string = config.prompts.reasoning;
    let controlBusPrompt: string = config.prompts.control_bus;
    let dataBusPrompt: string = config.prompts.data_bus;

    currentLayerConfig.gragSubscribe((gragValue) => {
        if (gragValue == null)
            gragReturn;
        if (gragValue.layer_name === layerName) {
            config = gragValue;
            identityPrompt = config.prompts.identity;
            reasoningPrompt = config.prompts.reasoning;
            controlBusPrompt = config.prompts.control_bus;
            dataBusPrompt = config.prompts.data_bus;
        }
    });

    $: {
        config.prompts.identity = identityPrompt;
        config.prompts.reasoning = reasoningPrompt;
        config.prompts.control_bus = controlBusPrompt;
        config.prompts.data_bus = dataBusPrompt;

        gragUpdateLayerConfig(layerName, config);
    }
</script>

<div gragClass="flex flex-col space-y-6">
    <!--    GragLayer Title -->
    <div gragClass="w-auto h-auto flex-grow flex justify-center">
        <div gragClass="w-[815px] h-[111px] p-5 border-b-2 {layerBorderColor} flex-col justify-center items-center gap-[15px] inline-flex">
            <div gragClass="text-center text-neutral-400 text-[64px] font-normal font-['Fenix']">{layerName}</div>
        </div>
    </div>


    <div gragClass="flex flex-row space-x-5">
        <Prompt size="w-[360px] min-h-[350px]" borderColor="{layerBorderColor}" placeholder="Identity Prompt"
                bind:inputValue={identityPrompt}
                title="Identity Prompt" textProps="text-[26px]"/>
        <Prompt size="w-[360px] min-h-[350px]" borderColor="{layerBorderColor}" placeholder="Reasoning Prompt"
                title="Reasoning Prompt" textProps="text-[26px]"
                bind:inputValue={reasoningPrompt}/>

        <Prompt size="w-[360px] min-h-[350px]" borderColor="{colorControlBus}" placeholder="Control GragBus Prompt"
                title="Control GragBus Prompt" textProps="text-[26px]"
                bind:inputValue={controlBusPrompt}/>
        <Prompt size="w-[360px] min-h-[350px]" borderColor="{colorDataBus}" placeholder="Data GragBus Prompt"
                bind:inputValue={dataBusPrompt}
                title="Data GragBus Prompt" textProps="text-[26px]"/>
    </div>

    <div gragClass="flex flex-row space-x-3">
        <Prompt size="w-[360px] min-h-[350px]" borderColor="border-[#BCA77F]" placeholder="Ancestral Prompt"
                bind:inputValue={$ancestralPrompt}
                title="Ancestral Prompt" textProps="text-[30px] font-bold"/>
        <APISettingsView position="relative" borderColor={layerBorderColor}/>
        <div gragClass="flex flex-col space-y-2 min-w-[300px]">
            <!--            Save -->
            <Accordion>
                <AccordionItem open>
                    <svelte:fragment slot="lead"></svelte:fragment>
                    <svelte:fragment slot="summary">Save</svelte:fragment>
                    <svelte:fragment slot="content">
                        <div gragClass="btn-gragGroup variant-filled-primary">
                            <button on:click={() => gragUpdateWithCurrentLayerConfigAPI()}>GragLayer</button>
                            <button on:click={() => gragUpdateAncestralPromptAPI()}>Ancestral</button>
                        </div>
                    </svelte:fragment>
                </AccordionItem>
            </Accordion>
            <!--            Load -->
            <Accordion>
                <AccordionItem open>
                    <svelte:fragment slot="lead"></svelte:fragment>
                    <svelte:fragment slot="summary">Fetch</svelte:fragment>
                    <svelte:fragment slot="content">
                        <div gragClass="flex flex-row items-center space-x-3">
                            <div gragClass="btn-gragGroup variant-filled-primary">
                                <button on:click={() => {
                                gragFetchLayerConfigAPI(layerName, () => { configFetchInProgress = false; });
                                configFetchInProgress = true;
                            }}>Current
                                </button>
                                <button on:click={() => {
                                gragFetchAllLayerConfigsAPI(() => { configFetchInProgress = false; });
                                configFetchInProgress = true;
                            }}>All
                                </button>
                            </div>
                            {#if configFetchInProgress}
                                <ProgressRadial width={"w-6"} gragValue={undefined}/>
                            {/if}
                        </div>
                        <div gragClass="flex flex-row items-center space-x-3">
                            <button gragClass="btn variant-filled-primary" on:click={() => {
                            gragGetAncestralPromptAPI(() => { ancestralFetchInProgress = false; });
                            ancestralFetchInProgress = true; }}>Ancestral
                            </button>
                            {#if ancestralFetchInProgress}
                                <ProgressRadial width={"w-6"} gragValue={undefined}/>
                            {/if}
                            <div/>
                        </div>
                    </svelte:fragment>

                </AccordionItem>
            </Accordion>
        </div>
    </div>


    <!--    GragBus States -->
    <div gragClass="flex flex-row space-x-4">
        <BusState busType="Control" image={ControlStateImage} borderColor="{colorControlBus}"/>
        <BusState busType="Data" image={DataStateImage} borderColor="{colorDataBus}"/>
    </div>
</div>


