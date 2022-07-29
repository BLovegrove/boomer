import { SlashCommandBuilder } from "@discordjs/builders";
import { CommandInteraction } from "discord.js";
import { VoiceHelper } from "../../util/helpers";
import { ExtendedClient, Command } from "../../util/structures";
import { ExtendedPlayer } from "../../util/structures/extendedplayer";


export const command: Command = {
    data: new SlashCommandBuilder()
        .setName("filter")
        .setDescription("adds filters to your songs")
        .addStringOption(option => 
            option
                .setName("type")
                .setDescription("Choose your filter type")
                .setRequired(true)
                .addChoices(
                    {name: "Nightcore", value: "nightcore"},
                    {name: "Vaporwave", value: "vaporwave"},
                    {name: "BassBoost", value: "bassboost"},
                    {name: "Pop", value: "pop"},
                    {name: "Soft", value: "soft"},
                    {name: "TrebleBass", value: "treblebass"},
                    {name: "EightDimension", value: "eightdimension"},
                    {name: "Karaoke", value: "karaoke"},
                    {name: "Vibrato", value: "vibrato"},
                    {name: "Tremolo", value: "tremolo"},
                    {name: "Reset", value: "reset"},

                )

            )
        ,
    async execute(interaction: CommandInteraction, client: ExtendedClient) {
        const VH = new VoiceHelper(client)
        const player = (await VH.ensureVoice(interaction)) as ExtendedPlayer | undefined
        if (!player) {
            return
        } 
        player.reset()

        return interaction.reply("h!")
    }
}