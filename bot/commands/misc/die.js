
const { SlashCommandBuilder } = require('@discordjs/builders');
const { Permissions, CommandInteraction } = require('discord.js');


module.exports = {
    data: new SlashCommandBuilder()
        .setName('die')
        .setDescription('Kills boomer. Restart him via (TO BE IMPLEMENTED) web portal.')
        .setDefaultMemberPermissions(Permissions.FLAGS.ADMINISTRATOR),

    /**@param {CommandInteraction} interaction*/
    async execute(interaction) {
        await interaction.reply({ content: "My battery is low and it's getting dark :(" })
    }
};