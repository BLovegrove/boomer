import { ExtendedClient, ClientEvent } from "../../util/structures";

export const event: ClientEvent = {
    name: "ready",
    async listen(client: ExtendedClient) {

        // add one-time listener for login alert
        client.once("ready", () => {
            if (client.user && client.manager) {
                console.log("Initialising lava manager...")
                client.manager.init(client.user.id);
                console.log(`${client.user.tag} is online.`)
            }
            else {
                console.log("Failed to init lava manager / discord client.");
            }
        })
    }
}