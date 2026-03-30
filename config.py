import json
import os
import logging

logger = logging.getLogger(__name__)

CONFIG_FILE = os.environ.get("ANALYTICS_CONFIG", os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json"))

_DEFAULT_CONFIG = {
    "ton_contracts": {
        "Catizen": "EQAnbLTnSI6rwqmvKwWge2rWpkG24cDTS0l5D1blnaiMDdME",
        "Notcoin": "EQDs6p5X2VfOPhQEqSrkpSrkpSrkpSrkpSrkpSrkpSrkyP6A",
        "Hamster Kombat": "EQDn8p9X2VfOPhQEqSrkpSrkpSrkpSrkpSrkpSrkpSrkyP6A", # Placeholder
        "Blum": "EQBlum_placeholder_address",
        "Major": "EQMajor_placeholder_address",
        "X Empire": "EQMusk_empire_placeholder",
        "MemeFi": "EQMemefi_placeholder",
        "TapSwap": "EQTapswap_placeholder",
        "Yescoin": "EQYescoin_placeholder",
        "PixelTap": "EQPixeltap_placeholder",
        "DeDust": "EQBf8uEZZar_E_E_placeholder",
        "STON.fi": "EQA_stonfi_placeholder",
        "Tonkeeper": "EQ_tonkeeper_app_address",
        "Fragment": "EQ_fragment_placeholder",
        "Getgems": "EQ_getgems_contract",
        "Storm Trade": "EQStormTrade_placeholder",
        "Evaa Protocol": "EQEvaa_placeholder",
    },
    "tg_channels": {
        "Catizen": "CatizenAnn",
        "Notcoin": "notcoin",
        "Hamster Kombat": "hamster_kombat",
        "Blum": "blumcrypto",
        "Major": "major",
        "X Empire": "empiremusk",
        "MemeFi": "memefi_coin",
        "TapSwap": "tapswapai",
        "Yescoin": "the_yescoin",
        "PixelTap": "pixeltap_xyz",
        "DeDust": "dedust_en",
        "STON.fi": "stonfidex",
        "Tonkeeper": "tonkeeper",
        "Fragment": "fragment",
        "Getgems": "getgemsinfo",
        "Storm Trade": "stormtrade",
        "Lost Dogs": "lostdogs",
        "Banana": "banana_mini_app",
        "TonSpace": "tonspace",
        "PocketFi": "pocketfi",
    },
    "app_categories": {
        "Gaming": ["Catizen", "Hamster Kombat", "Notcoin", "Blum", "X Empire", "MemeFi", "TapSwap", "Yescoin", "PixelTap", "Lost Dogs", "Banana"],
        "DeFi": ["DeDust", "STON.fi", "Storm Trade", "Evaa Protocol", "PocketFi"],
        "Utilities": ["Wallet", "Fragment", "Getgems", "Tonkeeper", "TonSpace"],
        "Social": ["Major"]
    },
    "top_apps": ["Hamster Kombat", "Blum", "Catizen", "Notcoin", "Major", "X Empire", "MemeFi", "TapSwap"],
    "trend_score_cap": 200,
}


def load_config():
    env_contracts = os.environ.get("TON_CONTRACTS")
    env_channels = os.environ.get("TG_CHANNELS")

    if env_contracts or env_channels:
        cfg = dict(_DEFAULT_CONFIG)
        if env_contracts:
            try:
                cfg["ton_contracts"] = json.loads(env_contracts)
            except json.JSONDecodeError:
                logger.warning("Неверный формат TON_CONTRACTS, используются значения по умолчанию")
        if env_channels:
            try:
                cfg["tg_channels"] = json.loads(env_channels)
            except json.JSONDecodeError:
                logger.warning("Неверный формат TG_CHANNELS, используются значения по умолчанию")
        return cfg

    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                file_cfg = json.load(f)
            merged = dict(_DEFAULT_CONFIG)
            merged.update(file_cfg)
            return merged
        except (json.JSONDecodeError, IOError) as e:
            logger.warning("Ошибка чтения config.json: %s, используются значения по умолчанию", e)

    return dict(_DEFAULT_CONFIG)


CONFIG = load_config()
