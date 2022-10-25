import { Client, ClientOptions, Collection } from "discord.js";
import { Manager } from "erela.js";
import { Command } from "./command";
import config from "../../config.json"
import { CommandHandler } from "../handlers/command";
import path from "path"

export class ExtendedClient extends Client {

    commands: Collection<String, Command>
    manager: Manager
    private _playerExists: boolean
    private _isDevMode: boolean

    constructor(options: ClientOptions, manager: Manager) {
        super(options);
        
        this.manager = manager
        this._playerExists = false
        this._isDevMode = config.dev.token != ""
        
        // grab the command files and generate a collection from them
        this.commands = CommandHandler.load(path.join(__dirname, "../../commands"))
        // register the commands with the discord API to display them on the server
        CommandHandler.register(this, this.commands)
    }

    get playerExists() {
        this._playerExists = this.manager.players.size != 0 ? true : false
        return this._playerExists
    }

    get isDevMode() {
        return this._isDevMode
    }

    async connect() {
        if (this.isDevMode) {
            await this.login(config.dev.token)
        } else {
            await this.login(config.bot.token);
        }
    };
};