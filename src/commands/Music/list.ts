import { SlashCommandBuilder } from "@discordjs/builders";
import { CommandInteraction } from "discord.js";
import { VoiceHelper } from "../../util/helpers";
import { ExtendedClient, Command, ListEmbedBuilder } from "../../util/structures";

export const command: Command = {
    data: new SlashCommandBuilder()
        .setName("list")
        .setDescription("Displays an interactive queue listing! Click the buttons to cycle through pages.")
        .addNumberOption(option => 
            option
                .setName("page")
                .setDescription("Page of the queue you want to list off. If you're unsure, just leave this blank.")
        )
        ,
    async execute(interaction: CommandInteraction, client: ExtendedClient) {
        var listPage = interaction.options.getNumber("page")
        if (!listPage) {
            listPage = 1
        }

        const VH = new VoiceHelper(client)
        const player = await VH.ensureVoice(interaction)
        if (!player) {
            return
        }

        var embed = new ListEmbedBuilder(player, listPage).toJSON()
        await interaction.reply({embeds:[embed]})

        return
    }
}