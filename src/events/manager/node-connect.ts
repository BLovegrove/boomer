import { ExtendedClient, ClientEvent } from "../../util/structures";

export const event: ClientEvent = {
    name: "",
    async listen(client: ExtendedClient) {

        // fires on successful connection to lavalink client node
        client.manager.once("nodeConnect", node => {
            console.log(`Node '${node.options.identifier}' is online.`)
        })
    }
}