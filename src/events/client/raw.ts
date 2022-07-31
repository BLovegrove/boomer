import { ExtendedClient, ClientEvent } from "../../util/structures";

export const command: ClientEvent = {
    name: "raw",
    async listen(client: ExtendedClient) {

        // THIS IS REQUIRED. Send raw events to Erela.js
        client.on("raw", d => client.manager.updateVoiceState(d));
    }
}