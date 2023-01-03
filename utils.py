def strip_tag(instr: str) -> str:
    if (pos := instr.find(">")) != -1:
        instr = instr[pos + 1 :]
    if (pos := instr.rfind("<")) != -1:
        instr = instr[:pos]
    return instr


def parse_url(url: str) -> tuple[list[str], dict[str, str]]:
    """Разбирает url на составляющие адреса [str]
    и словарь параметров [dict]

    Args:
        url (str): url для разбора

    Returns:
        tuple[[str], dict[str,str]]: _
    """
    return (
        ([url], {})
        if not (param_begin := url.rfind("?"))
        else (
            [url[:param_begin]],
            {
                key: value
                for (key, value) in [
                    param_value.split("=", 1)
                    for param_value in url[param_begin + 1 :].split("&")
                ]
            },
        )
    )


from typing import Any


def merge_url(url: str | list[str], params: dict[str, Any]) -> str:
    url = "".join(url) if isinstance(url, list) else url
    return (
        url.strip()
        + "?"
        + "&".join([f"{key.strip()}={value}" for key, value in params.items()])
    )
