import Header from "../components/Header.jsx";
import {useOutletContext} from "react-router-dom";
import useLibrary from "../hooks/useLibrary.js";
import {useEffect, useState} from "react";
import "./Games.css";




export default function Games() {

    const [excluindo, setExcluindo] = useState({});
    const [idsExcluidos, setIdsExcluidos] = useState([]);
    const [erroExclusao, setErroExclusao] = useState("");


    const context = useOutletContext();
    const user = context?.user;

    const {
        fullContent,
        libraryError,
        loadingLibrary,
    } = useLibrary(user?.id);

    const [statusAtualizados, setStatusAtualizados] = useState({});
    const [atualizando, setAtualizando] = useState({});
    const [erroStatus, setErroStatus] = useState("");

    useEffect(() => {
        setStatusAtualizados({});
        setAtualizando({});
        setErroStatus("");
    }, [user?.id]);

    async function alternarStatus(jogo) {
        const id = jogo.registroId;

        if (atualizando[id]) return;

        const novoStatus =
            jogo.statusUsuario === "Quero Jogar"
                ? "Jogado"
                : "Quero Jogar";

        setErroStatus("");
        setAtualizando((anterior) => ({
            ...anterior,
            [id]: true,
        }));

        try {
            const response = await fetch(
                `http://localhost:8000/library/${id}`,
                {
                    method: "PATCH",
                    credentials: "include",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        status: novoStatus,
                    }),
                }
            );

            if (!response.ok) {
                const erro = await response.json().catch(() => null);

                throw new Error(
                    typeof erro?.detail === "string"
                        ? erro.detail
                        : `Não foi possível alterar o status (${response.status}).`
                );
            }

            const dados = await response.json();

            // Usa o status confirmado pelo backend.
            setStatusAtualizados((anterior) => ({
                ...anterior,
                [id]: dados.status,
            }));
        } catch (error) {
            setErroStatus(error.message);
        } finally {
            setAtualizando((anterior) => ({
                ...anterior,
                [id]: false,
            }));
        }
    }

    async function excluirConteudo(registroId) {
        if (excluindo[registroId]) return;

        setErroExclusao("");
        setExcluindo((anterior) => ({
            ...anterior,
            [registroId]: true,
        }));

        try {
            const response = await fetch(
                `http://localhost:8000/library/${registroId}`,
                {
                    method: "DELETE",
                    credentials: "include",
                }
            );

            if (!response.ok) {
                const erro = await response.json().catch(() => null);

                throw new Error(
                    typeof erro?.detail === "string"
                        ? erro.detail
                        : `Não foi possível excluir o conteúdo (${response.status}).`
                );
            }


            setIdsExcluidos((anterior) => [
                ...anterior,
                registroId,
            ]);
        } catch (error) {
            setErroExclusao(error.message);
        } finally {
            setExcluindo((anterior) => ({
                ...anterior,
                [registroId]: false,
            }));
        }
    }


    if (!user || user.id == null) {
        return <p>Usuário não identificado.</p>;
    }

    if (loadingLibrary) {
        return <p>Carregando jogos...</p>;
    }

    if (libraryError) {
        return <p role="alert">{libraryError}</p>;
    }

    const conteudosPorId = new Map(
        fullContent.map((conteudo) => [
            String(conteudo._id),
            conteudo,
        ])
    );

    const jogos = (user.content ?? [])
        .filter((registro) => !idsExcluidos.includes(registro.id))
        .flatMap((registro) => {
            const conteudo = conteudosPorId.get(
                String(registro.mongo_id)
            );

            if (!conteudo || conteudo.type !== "game") {
                return [];
            }

            return [{
                ...conteudo,
                registroId: registro.id,
                statusUsuario:
                    statusAtualizados[registro.id] ?? registro.status,
                notaUsuario: registro.rating,
            }];
        });

    const colunas = [
        {
            id: "watchlist-title",
            titulo: "Quero jogar",
            classeStatus: "status-pending",
            jogos: jogos.filter(
                (jogo) => jogo.statusUsuario === "Quero Jogar"
            ),
        },
        {
            id: "watched-title",
            titulo: "Jogados",
            classeStatus: "status-watched",
            jogos: jogos.filter(
                (jogo) => jogo.statusUsuario === "Jogado"
            ),
        },
    ];

    return (
        <>
            <Header />

            <div className="games-page">
                <main className="games-content">
                    <section
                        className="games-heading"
                        aria-labelledby="games-title"
                    >
                        <div>
                            <h1 id="games-title">🎬 Meus jogos</h1>
                            <p>
                                Organize o que quer jogar e acompanhe o que já jogou.
                            </p>
                        </div>

                        <button className="add-game-button" type="button">
                            + Adicionar jogo
                        </button>
                    </section>

                    {erroStatus && (
                        <p role="alert">{erroStatus}</p>
                    )}

                    <div className="games-columns">
                        {colunas.map((coluna) => (
                            <section
                                key={coluna.id}
                                className="game-column"
                                aria-labelledby={coluna.id}
                            >
                                <header className="column-header">
                                    <h2 id={coluna.id}>
                    <span
                        className={`status-dot ${coluna.classeStatus}`}
                        aria-hidden="true"
                    />
                                        {coluna.titulo}
                                    </h2>

                                    <span className="game-count">
                    {coluna.jogos.length}{" "}
                                        {coluna.jogos.length === 1
                                            }
                  </span>
                                </header>

                                {coluna.jogos.length === 0 ? (
                                    <p>Nenhum jogo nesta lista.</p>
                                ) : (
                                    <ul className="game-list">
                                        {coluna.jogos.map((jogo) => {
                                            const salvando = Boolean(
                                                atualizando[jogo.registroId]
                                            );

                                            const acao =
                                                jogo.statusUsuario === "Quero Jogar"
                                                    ? "Marcar como jogado"
                                                    : "Mover para quero jogar";

                                            return (
                                                <li key={jogo.registroId}>
                                                    <article className="game-card">
                                                        <div className="game-poster">
                                                            <img
                                                                src={jogo.poster}
                                                                alt={`Capa de ${jogo.title}`}
                                                            />
                                                        </div>

                                                        <div className="game-info">
                                                            <h3>{jogo.title}</h3>

                                                            <p className="game-year">
                                                                {jogo.date?.slice(0, 4)}
                                                            </p>

                                                            <ul
                                                                className="game-genres"
                                                                aria-label="Gêneros"
                                                            >
                                                                {(jogo.genres ?? []).map(
                                                                    (genero, index) => (
                                                                        <li key={`${genero}-${index}`}>
                                                                            {genero}
                                                                        </li>
                                                                    )
                                                                )}
                                                            </ul>
                                                        </div>

                                                        <div className="game-actions">
                                                            <button
                                                                type="button"
                                                                onClick={() => excluirConteudo(jogo.registroId)}
                                                                disabled={
                                                                    excluindo[jogo.registroId] ||
                                                                    atualizando[jogo.registroId]
                                                                }
                                                                aria-label={`Excluir ${jogo.title} da biblioteca`}
                                                            >
                                                                x
                                                            </button>

                                                            <button
                                                                type="button"
                                                                onClick={() => alternarStatus(jogo)}
                                                                disabled={salvando}
                                                                aria-label={acao}
                                                                title={acao}
                                                                aria-busy={salvando}
                                                            >
                                                                {salvando ? "…" : "⋮"}
                                                            </button>
                                                        </div>
                                                    </article>
                                                </li>
                                            );
                                        })}
                                    </ul>
                                )}
                            </section>
                        ))}
                    </div>
                </main>
            </div>
        </>
    );
}