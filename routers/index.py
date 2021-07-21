from fastapi import status
from fastapi.responses import HTMLResponse

from . import router


def html_response():
    html_content = """
        <html>
            <head><title>The MES College Alumni Association &#174;</title></head>
            <body style="color: #202020; font-family: sans-serif;">
                <div style="text-align: center; margin-top: 100px">
                    <img src='https://ik.imagekit.io/pwxm960evbp/tr:w-400/MES-AA/Site_Images/logo_LdmkTP9ua.png' alt='logo' />
                    <p style="font-size: 1.5rem;">The MES College Alumni Association <span style="vertical-align: super;">&#174;</span></p>

                    <a style="cursor: pointer; font-size: 1.2rem; text-decoration: none; color: #202020;" href="https://mesalumniassociation.com">mesalumniassociation.com</a>
                </div>
            </body>
        </html>
    """

    return HTMLResponse(content=html_content, status_code=200)


@router.get("/", status_code=status.HTTP_200_OK)
async def return_html_response():
    return html_response()
