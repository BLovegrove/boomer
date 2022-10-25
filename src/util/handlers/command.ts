import { REST } from "@discordjs/rest";
import { Collection } from "discord.js";
import { Command, ExtendedClient } from "../structures";
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

    static async register(client: ExtendedClient, commands: Collection<String, Command>) {

        const rest = new REST({ version: '9' })

        if (client.isDevMode) {
            rest.setToken(config.dev.token);
        } else {
            rest.setToken(config.bot.token);
        }

        try {
            console.log('Started refreshing guild application (/) commands.');

            const commandsData: any[] = []
            commands.forEach(command => {
                if (client.isDevMode) {
                    (command.data as SlashCommandBuilder).setDefaultMemberPermissions(config.dev.permissionFlag)
                }
                commandsData.push(command.data.toJSON())
            })
            
            // set guild commands / clear global commands
            if (client.isDevMode) {
                await rest.put(Routes.applicationCommands(config.dev.clientID), { body: {} });
                await rest.put(Routes.applicationGuildCommands(config.dev.clientID, config.bot.guildID), { body: commandsData });

            } else {
                await rest.put(Routes.applicationCommands(config.bot.clientID), { body: {} });
                await rest.put(Routes.applicationGuildCommands(config.bot.clientID, config.bot.guildID), { body: commandsData });
            }

            console.log('Successfully reloaded guild slash commands.');
        } catch (error) {
            console.error(error);
        }
    }

    static async deRegister(client: ExtendedClient) {
        if (client.isDevMode) {
            const rest = new REST({ version: '9' }).setToken(config.dev.token);

            // clear all commands
            await rest.put(Routes.applicationGuildCommands(config.dev.clientID, config.bot.guildID), { body: {} });
            await rest.put(Routes.applicationCommands(config.dev.clientID), { body: {} });
        }
    }
}