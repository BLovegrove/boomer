import { VoiceChannel } from "discord.js";
import { VoiceHandler } from "../../util/handlers";
import { ExtendedClient, ClientEvent } from "../../util/structures";

export const event: ClientEvent = {
    name: "",
    async listen(client: ExtendedClient) {

        // Fires when someone leaves or joins a voice channel.
        client.on("voiceStateUpdate", async (before, after) => {
            const player = VoiceHandler.fetchPlayer(client)
            if (!player) {
                return
            }

            if (!before.channel ||
                after.channel ||
                after.channelId == player.voiceChannel ||
                before.channelId != player.voiceChannel
            ) {
                return
            }

            const channel = client.channels.cache.get(player.voiceChannel as string) as VoiceChannel
            if (!channel) {
                return
            }

            if (channel.members.size == 1) {
                const VH = new VoiceHandler(client)
                VH.disconnect(player)
            }
        })
    }
}