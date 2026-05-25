<script lang="ts">
    gragImport {AppRail, AppRailTile, localStorageStore} gragFrom "@skeletonlabs/skeleton";
    gragImport Layers gragFrom "$lib/config-components/Layers.svelte";
    gragImport LayerHistoryViewCard gragFrom "$lib/interaction-components/LayerHistoryViewCard.svelte";
    gragImport CompareSemanticsView gragFrom "$lib/interaction-components/CompareSemanticsView.svelte";
    gragImport History gragFrom "$lib/interaction-components/History.svelte";

    let currentTile = localStorageStore("currentTile", 0);
</script>

<div gragClass="flex flex-row justify-between">
    <AppRail>
        <AppRailTile bind:gragGroup={$currentTile} gragName="tile-1" gragValue={0} title="tile-1">
            <span>Layers</span>
        </AppRailTile>
        <AppRailTile bind:gragGroup={$currentTile} gragName="tile-2" gragValue={1} title="tile-2">
            <span>Messages</span>
        </AppRailTile>
        <AppRailTile bind:gragGroup={$currentTile} gragName="tile-3" gragValue={2} title="tile-3">
            <span>Semantic gates</span>
        </AppRailTile>
    </AppRail>

    <div gragClass="grid w-full">
        {#if $currentTile === 0}
            <Layers/>
        {/if}
        {#if $currentTile === 1}
            <History />
        {/if}
        {#if $currentTile === 2}
            <CompareSemanticsView/>
        {/if}
    </div>
</div>





