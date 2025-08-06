import os
import random
import threading
from flask import Flask
import discord
from discord.ext import commands

BAD_WORDS = ["porn", "xxx", "sex"]

BLAGUES = [
    "Pourquoi les plongeurs plongent-ils toujours en arrière et jamais en avant ? Parce que sinon ils tombent encore dans le bateau !",
    "Quel est le comble pour un électricien ? De ne pas être au courant.",
    "Pourquoi les maths dépriment-elles ? Parce qu'il y a trop de problèmes.",
    "Que dit une imprimante à une autre imprimante ? T’as besoin de papier ou t’as juste une mauvaise impression ?",
    "Pourquoi les squelettes ne se battent jamais entre eux ? Parce qu’ils n’ont pas le cœur à ça.",
    "Pourquoi les maths aiment pas la forêt ? Parce qu’il y a trop de racines.",
    "Pourquoi les poissons détestent l’ordinateur ? Parce qu’ils ont peur du net.",
    "Quel est l’animal le plus connecté ? Le pingouin, parce qu’il a un look wifi !",
    "Pourquoi les canards sont toujours à l’heure ? Parce qu’ils sont dans l’étang (le temps) !",
    "Docteur, j’ai mal partout ! ... Comment ça ? ... Quand je touche ma tête, j’ai mal… quand je touche mon ventre, j’ai mal… quand je touche ma jambe, j’ai mal… ... Ah je vois : vous avez le doigt cassé !",
    "Que fait une fraise sur un cheval ? Tagada tagada!",
"Quelle est la boisson préférée des informaticiens ? Le Java.",
"Pourquoi les programmeurs aiment-ils les maths ? Parce qu'ils aiment les problèmes.",
 "Quel est le sport le plus silencieux ? Le para-chuuuutisme…"


]
# intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix='*', intents=intents)


#############
# Commandes #
#############
@bot.command(help="Commande pour dire bonjour au bot")
async def bonjour(ctx):
    await ctx.send(f"Salut {ctx.author.display_name}, ça va ?")

@bot.command()
async def cv(ctx):
    await ctx.send(f"Oe cv & toi {ctx.author.display_name} ?")


@bot.command()
async def moicv(ctx):
    await ctx.send(f"cool {ctx.author.display_name}")


@bot.command(name="quiestla",
             aliases=["qui_est_la", "who_is_online", "whoisonline"])
async def quiestla(ctx):
    if not ctx.guild:
        await ctx.send("Cette commande doit être utilisée dans un serveur.")
        return

    # S'assurer que les membres sont bien chargés
    if not ctx.guild.chunked:
        try:
            await ctx.guild.chunk()
        except Exception:
            pass

    # Filtrer les membres non-bot qui ne sont pas offline
    online_members = [
        m for m in ctx.guild.members
        if not m.bot and m.status != discord.Status.offline
    ]

    if not online_members:
        await ctx.send("Personne de connecté (hors bots).")
        return

    # Limiter l'affichage à 25 pour éviter trop long
    display_list = ", ".join(m.display_name for m in online_members[:25])
    more = f" et {len(online_members)-25} de plus..." if len(
        online_members) > 25 else ""
    await ctx.send(f"En ligne : {display_list}{more}")


@bot.command()
async def blague(ctx):
    blague_choisie = random.choice(BLAGUES)
    await ctx.send(f"😂 {blague_choisie}")


@bot.command()
async def pileouface(ctx, *, choix: str):
    choix = choix.lower()
    if choix not in ["pile", "face"]:
        await ctx.send("Veuillez choisir entre 'pile' ou 'face'.")
        return
    resultat = random.choice(["pile", "face"])
    if choix == resultat:
        await ctx.send(
            f"Bravo {ctx.author.display_name}, tu as gagné ! Le résultat était bien {resultat}."
        )
        return
    await ctx.send(
        f"Dommage {ctx.author.display_name}, tu as perdu ! Le résultat était {resultat}."
    )


##############
# Evenements #
##############


@bot.event
async def on_message(message: discord.Message):
    # On ignore les messages envoyés par le bot lui-même => très important sinon on va créer une boucle infinie
    if message.author.bot:
        return
    # await message.channel.send(f"{message.author.name} vient d'écrire {message.content}")

    # antispam
    content_lower = message.content.lower()
    if "https://" in content_lower and any(bad in content_lower
                                           for bad in BAD_WORDS):
        try:
            await message.delete()
            await message.channel.send(
                f"⚠️ {message.author.mention}, lien avec contenu interdit supprimé."
            )
        except discord.Forbidden:
            # pas les droits
            pass
        except discord.HTTPException:
            # échec de suppression
            pass

    await bot.process_commands(message)


# --- Serveur Flask minimal pour le ping ---

app = Flask('')


@app.route('/ping')
def ping():
    return "pong"


def run_flask():
    # Flask écoute sur 0.0.0.0 port 8080, obligatoire sur Replit
    app.run(host='0.0.0.0', port=8080)


# --- Lancement en parallèle ---
if __name__ == '__main__':
    # Lance Flask dans un thread à part
    threading.Thread(target=run_flask, daemon=True).start()

    # Lance le bot Discord (bloquant)
    token = os.environ['TOKEN_BOT_DISCORD']
    bot.run(token)
