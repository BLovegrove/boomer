import { Player } from "erela.js";
import { ExtendedClient } from "../structures";
import { VoiceHandler } from "./voice";
import config from "../../config.json"
import { CommandInteraction } from "discord.js";
import { ClearedEmbedBuilder } from "../structures";

export class QueueHandler {

    private client: ExtendedClient
    private VH: VoiceHandler

    constructor(client: ExtendedClient) {
        this.client = client
        this.VH = new VoiceHandler(client)
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
            const cleared = player.queue.remove(index - 1).at(0)

            if (!cleared) {
                interaction.reply(config.error.trackNotFound)
                return
            }

            const embed = new ClearedEmbedBuilder(interaction, cleared, player, index).toJSON()
            await interaction.reply({embeds: [embed]})
        }
    }
}