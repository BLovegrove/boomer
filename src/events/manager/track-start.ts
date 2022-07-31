import { VoiceHandler } from "../../util/handlers";
import { ExtendedClient, ClientEvent } from "../../util/structures";

export const command: ClientEvent = {
    name: "trackStart",
    async listen(client: ExtendedClient) {

        // Fires whenever a new treack starts playing
        client.manager.on("trackStart", async node => {
            const player = VoiceHandler.fetchPlayer(client)
            if (player) {
                await VoiceHandler.updateStatus(client, player)
            }
        })
    }
}