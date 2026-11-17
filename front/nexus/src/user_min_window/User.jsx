import { Link, useNavigate } from "react-router-dom";
import { apiUrl } from "../api.js";
import { useEffect, useRef, useState } from "react";
import "./User.css";

export default function User({ usuario }) {
    const navigate = useNavigate();
    const [saindo, setSaindo] = useState(false);
    const [erroSaida, setErroSaida] = useState("");
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
        if (saindo) return;
        setSaindo(true);
        setErroSaida("");
        try {
            const response = await fetch(apiUrl("/logout"), {
                method: "POST",
                credentials: "include",
            });

            if (!response.ok) {
                throw new Error(`Erro ao sair: ${response.status}`);
            }

            setAberto(false);
            navigate("/login", { replace: true });
        } catch {
            setErroSaida("Não foi possível sair. Tente novamente.");
            setSaindo(false);
        }
    }


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
                    <Link to="/perfil" onClick={() => setAberto(false)}>Meu perfil</Link>
                    {/*<a href="/configuracoes">Configurações</a>*/}
                    <button type="button" disabled={saindo} onClick={() => logout()}>{saindo ? "Saindo…" : "Sair"}</button>
                    {erroSaida && <p role="alert">{erroSaida}</p>}
                </div>
            )}
        </div>
    );
}