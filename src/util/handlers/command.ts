import { REST } from "@discordjs/rest";
import { Collection } from "discord.js";
import { Command } from "../structures";
import fs from "fs";
import config from "../../config.json"
import { Routes } from "discord-api-types/v10";
import { SlashCommandBuilder } from "@discordjs/builders";


export class CommandHandler {

    // read commands dirs for command modules
    static load(commandPath: fs.PathLike) {
        // init empty commands collection

        const commands = new Collection<String, Command>();
        fs.readdirSync(commandPath).forEach(dir => {
            // both file.endswith needed for dev vs production running
            const files = fs.readdirSync(`${commandPath}/${dir}/`).filter(file => (file.endsWith('.js') || file.endsWith('.ts')));

            // add command module files to collection
            for (const file of files) {
                const { command } = require(`${commandPath}/${dir}/${file}`);
                commands.set(command.data.name, command);
            }
        });

        return commands;
    }

    static async register(commands: Collection<String, Command>) {

        const rest = new REST({ version: '9' })

        if (config.bot.devMode) {
            rest.setToken(config.dev.token);
        } else {
            rest.setToken(config.bot.token);
        }

        try {
            console.log('Started refreshing guild application (/) commands.');

            const commandsData: any[] = []
            commands.forEach(command => {
                if (config.bot.devMode) {
                    (command.data as SlashCommandBuilder).setDefaultMemberPermissions(config.dev.permissionFlag)
                }
                commandsData.push(command.data.toJSON())
            })
            
            // set guild commands / clear global commands
            if (config.bot.devMode) {
                await rest.put(Routes.applicationCommands(config.dev.clientID), { body: {} });
                await rest.put(Routes.applicationGuildCommands(config.dev.clientID, config.bot.guildID), { body: commandsData });

            } else {
                await rest.put(Routes.applicationCommands(config.bot.clientID), { body: {} });
                await rest.put(Routes.applicationGuildCommands(config.bot.clientID, config.bot.guildID), { body: commandsData });
            }

            console.log('Successfully reloaded guild application (/) commands.');
        } catch (error) {
            console.error(error);
        }
    }

    static async deRegister() {
        if (config.bot.devMode) {
            const rest = new REST({ version: '9' }).setToken(config.dev.token);

            // clear all commands
            await rest.put(Routes.applicationGuildCommands(config.dev.clientID, config.bot.guildID), { body: {} });
            await rest.put(Routes.applicationCommands(config.dev.clientID), { body: {} });
        }
    }
}