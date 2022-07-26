import { SlashCommandBuilder } from "@discordjs/builders";
import { CommandInteraction } from "discord.js";
import { VoiceHelper } from "../../util/helpers";
import { Boomer, Command, ListEmbedBuilder } from "../../util/structures";
import config from "../../config.json"
import { Track, TrackUtils, UnresolvedTrack } from "erela.js";

export const command: Command = {
    data: new SlashCommandBuilder()
        .setName("list")
        .setDescription("Displays an interactive queue listing! Click the buttons to cycle through pages.")
        .addStringOption(option =>
            option
                .setName("type")
                .setDescription("Loads different list (one for unre4solved tracks (spotify) one for resolved)")
                .setRequired(true)
                .addChoices(
                    {name: "safe", value:"safe"},
                    {name: "resolved", value: "resoilved"}
                )
        )
        .addNumberOption(option => 
            option
                .setName("page")
                .setDescription("Page of the queue you want to list off. If you're unsure, just leave this blank.")
        )
        ,
    async execute(interaction: CommandInteraction, client: Boomer) {
        const listType = interaction.options.getString("type", true)
        var listPage = interaction.options.getNumber("page")
        if (!listPage) {
            listPage = 1
        }

        const VH = new VoiceHelper(client)
        const player = await VH.ensureVoice(interaction)
        if (!player) {
            return
        }

        switch(listType) {
            case "safe":

                var embed = new ListEmbedBuilder(player, listPage).toJSON()
                interaction.reply({embeds:[embed]})

                return

            case "resolved":

                const listStart = (listPage - 1) * config.music.listPageLength
                const listEnd = listPage * config.music.listPageLength

                for (var i = listStart; i < listEnd; i++) {
                    var track = player.queue.at(i) as Track | UnresolvedTrack
                    if (!track) {
                        break
                    }

                    if (TrackUtils.isUnresolvedTrack(track)) {
                        await (track as UnresolvedTrack).resolve()
                    }
                }

                var embed = new ListEmbedBuilder(player, listPage).toJSON()
                interaction.reply({ embeds: [embed] })

                return
        }
    }
}