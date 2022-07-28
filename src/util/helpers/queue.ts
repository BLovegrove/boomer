import { Player } from "erela.js";
import { ExtendedClient } from "../structures";
import { VoiceHelper } from "./voice";
import config from "../../config.json"
import { CommandInteraction } from "discord.js";
import { ClearedEmbedBuilder } from "../structures";

export class QueueHelper {

    private client: ExtendedClient
    private VH: VoiceHelper

    constructor(client: ExtendedClient) {
        this.client = client
        this.VH = new VoiceHelper(client)
    }

    updatePages(player: Player) {
        player.set('pages', Math.ceil(player.queue.length / config.music.listPageLength))
    }

    async clear(interaction: CommandInteraction, index?: number) {
        const player = await this.VH.ensureVoice(interaction)
        if (!player) {
            return
        }

        if (!index) {
            player.queue.clear()
            player.set('pages', 0)
            interaction.reply(":boom: Queue cleared!")

        } else {
            const cleared = player.queue.remove(index).at(0)

            if (!cleared) {
                interaction.reply(config.error.trackNotFound)
                return
            }

            interaction.reply({embeds: [
                new ClearedEmbedBuilder(interaction, cleared, player).toJSON()
            ]})
        }
    }
}