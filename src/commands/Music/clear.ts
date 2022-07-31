import { SlashCommandBuilder } from "@discordjs/builders";
import { CommandInteraction } from "discord.js";
import { QueueHandler, VoiceHandler } from "../../util/handlers";
import { ExtendedClient, Command } from "../../util/structures";

export const command: Command = {
    data: new SlashCommandBuilder()
        .setName("clear")
        .setDescription("Clears the whole (or part of the) queue")
        .addNumberOption(option =>
            option
                .setName("index")
                .setDescription("Track you want to remove from the queue (check /list for those numbers)")
        )
        ,
    async execute(interaction: CommandInteraction, client: ExtendedClient) {
        const QH = new QueueHandler(client)
        const VH = new VoiceHandler(client)
        const player = await VH.ensureVoice(interaction)
        if (!player) {
            return
        }

        const index = interaction.options.getNumber('index')
        if (!index) {
            await QH.clear(interaction)
            return

        } else {
            if (index <= 0) {
                await interaction.reply({ content: ":warning: That index is too low! Queue starts at #1." , ephemeral: true})
                return

            } else if (index > player.queue.length) {
                await interaction.reply({content: `:warning: That index is too high! Queue only ${player.queue.length} items long`, ephemeral: true})
                return

            } else {
                await QH.clear(interaction, index)
                return
            }
        }
    }
}