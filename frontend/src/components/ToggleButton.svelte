<script>
    $: isSlotFilled = $$slots["default"];
    export let enable;
    export let onclick;
    export let disabled = false;
    export let icon;
</script>

<main>
    <button on:click={onclick} class:enable data-title="Enable proxy" disabled={disabled}>
        <span class="material-icons" class:icon-button-icon={!isSlotFilled}>
            {#if enable}
                {#if icon == "globe"}
                    location_on
                {:else}
                    cloud
                {/if}
            {:else}
                {#if icon == "globe"}
                    location_off
                {:else}
                    cloud_off
                {/if}
            {/if}
        </span>

        {#if isSlotFilled}
            <div>
                <slot></slot>
            </div>
        {/if}
    </button>
</main>

<style>
    button {
        background: transparent;
        color: white;
        display: flex;
        border-style: solid;
        border-color: white;
        border-width: 2px;
        opacity: 0.75;
        transition: 0.3s;
        padding: 10px;
        font-size: 1.25em;
        border-radius: 50px;
        margin: 0 5px 0 5px;
    }

    button:active {
        transform: scale(93%, 93%);
    }

    .disabled:active {
        transform: none;
    }

    button > span {
        color: inherit;
        padding-left: 5px;
        font-size: calc(var(--fontSize) + 0.2rem);
    }

    button div {
        margin: 10px;
    }

    button div:active {
        margin: 10px;
    }

    .icon-button-icon {
        padding: 0px;
        font-size: calc(var(--fontSize) + 0.2rem);
    }

    button:hover {
        opacity: 1;
    }
</style>