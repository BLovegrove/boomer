import { SlashCommandBuilder } from "@discordjs/builders";
import { CommandInteraction } from "discord.js";
import { VoiceHandler } from "../../util/handlers";
import { ExtendedClient, Command } from "../../util/structures";
import { ExtendedPlayer } from "../../util/structures/extended-player";


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
                    {name: "Reset", value: "reset"}
                )
        )
        ,
    async execute(interaction: CommandInteraction, client: ExtendedClient) {
        const VH = new VoiceHandler(client)
        const player = (await VH.ensureVoice(interaction)) as ExtendedPlayer | undefined
        if (!player) {
            return
        } 
        const filterType = interaction.options.getString("type",true)
        switch (filterType) {
            case "nightcore": {
                player.nightcore = true;
                break
            }
            case "vaporwave": {
                player.vaporwave = true;
                break
            }
            case "bassboost": {
                player.bassboost = true;
                break
            }
            case "pop": {
                player.pop = true;
                break
            }
            case "soft": {
                player.soft = true;
                break
            }
            case "treblebass": {
                player.treblebass = true;
                break
            }
            case "eightdimension": {
                player.eightdimension = true;
                break
            }
            case "karaoke": {
                player.karaoke = true;
                break
            }
            case "vibrato": {
                player.vibrato = true;
                break
            }
            case "tremolo": {
                player.tremolo = true;
                break
            }
            case "reset": {
                player.reset()
                break
            }
        }
        const filterName = filterType.at(0)!.toUpperCase() + filterType.slice(1)
        await interaction.reply(`${filterName} filter applied. Please wait a few seconds for it to kick in.` )
    }
}