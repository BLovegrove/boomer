import { ExtendedClient, ClientEvent } from "../../util/structures";

export const command: ClientEvent = {
    name: "nodeError",
    async listen(client: ExtendedClient) {
        
        // Emitted whenever a node encountered an error
        client.manager.on("nodeError", (node, error) => {
            console.log(`Node "${node.options.identifier}" encountered an error: ${error.message}.`)
        })
    }
}