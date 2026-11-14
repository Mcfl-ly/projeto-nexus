import { useEffect, useRef, useState } from "react";
import "./User.css";

export default function User({ usuario }) {
    const [aberto, setAberto] = useState(false);
    const perfilRef = useRef(null);
    const botaoRef = useRef(null);

    useEffect(() => {
        function clicarFora(evento) {
            if (!perfilRef.current?.contains(evento.target)) {
                setAberto(false);
            }
        }

        function pressionarTecla(evento) {
            if (evento.key === "Escape") {
                setAberto(false);
                botaoRef.current?.focus();
            }
        }

        if (!aberto) return;

        document.addEventListener("pointerdown", clicarFora);
        document.addEventListener("keydown", pressionarTecla);

        return () => {
            document.removeEventListener("pointerdown", clicarFora);
            document.removeEventListener("keydown", pressionarTecla);
        };
    }, [aberto]);

    async function logout() {
        try {
            const response = await fetch("http://localhost:8000/logout", {
                method: "POST",
                credentials: "include",
            });

            if (!response.ok) {
                throw new Error(`Erro ao sair: ${response.status}`);
            }

            setAberto(false);
            window.location.assign("/login");
        }   catch (erro) {
        console.error("Erro no logout:", erro);
    }}


    return (
        <div className="perfil" ref={perfilRef}>
            <button
                ref={botaoRef}
                className="perfil-botao"
                type="button"
                aria-label="Opções do perfil"
                aria-expanded={aberto}
                aria-controls="perfil-janela"
                onClick={() => setAberto((atual) => !atual)}
            >
                👤
            </button>

            {aberto && (
                <div id="perfil-janela" className="perfil-janela">
                    <p>Olá, bem-vindo <strong>{`${usuario}`}</strong>!</p>
                    <a href="/perfil">Meu perfil</a>
                    {/*<a href="/configuracoes">Configurações</a>*/}
                    <button type="button" onClick={() => logout()}>Sair</button>
                </div>
            )}
        </div>
    );
}