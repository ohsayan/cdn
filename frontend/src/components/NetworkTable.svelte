<script>
    import {onMount} from "svelte";

    let nodes;
    let nodeNum;
    export let admin = false;

    function getNodes() {
        fetch("https://dash.delivr.dev/api/nodes/list", {
            credentials: "include"
        })
            .then(response => response.json())
            .then(data => {
                nodes = data["message"]
                nodeNum = data["message"].length
            })
    }

    onMount(() => getNodes());
</script>

<main>
    <div class="table-wrapper">
        <table class="sethjs-table">
            <thead>
            <tr>
                <th>Name ({nodeNum})</th>
                <th>Location</th>
                <th>Datacenter</th>
                <th>Provider</th>
                {#if admin}
                    <th>IP</th>
                {/if}
            </tr>
            </thead>

            <tbody>
            {#if nodes}
                {#each nodes as node, i }
                    <tr>
                        <td>{node["name"]}</td>
                        <td>{node["location"]}</td>
                        <td>{node["datacenter"]}</td>
                        <td>{node["provider"]}</td>
                        {#if admin}
                            <td>{node["management_ip"]}</td>
                        {/if}
                    </tr>
                {/each}
            {:else}
                <p style="padding-left: 10px">Loading...</p>
            {/if}
            </tbody>
        </table>
    </div>
</main>

<style>
    main {
        border: 2px solid white;
        border-radius: 15px;
        height: 100%;
    }

    div {
        display: flex;
        justify-content: space-between;
    }

    span {
        margin: 10px;
    }

    h2 {
        margin: 15px;
    }

    :global(.sethjs-table th) {
        padding-top: 16px;
        padding-bottom: 16px;
        padding-left: 20px;
        text-align: left;
        background-color: #202020;
        border-bottom: 1px solid #555555;
        color: white;
        margin: 0;
    }

    :global(.sethjs-table tr) {
        width: 100%;
    }

    :global(.sethjs-table tr:nth-child(odd)) {
        background-color: #111111;
    }

    :global(.sethjs-table td) {
        padding-top: 15px;
        padding-bottom: 15px;
        padding-left: 20px;
        text-align: left;
    }

    .table-wrapper {
        width: 100%;
    }

    tbody {
        overflow-y: auto;
        max-height: calc(400px - 65px);
        display: block;
    }

    thead, tbody tr {
        display: table;
        width: 100%;
    }
</style>
