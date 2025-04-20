package school.sptech.menor_tempo_atendimento.dto;

import school.sptech.menor_tempo_atendimento.domain.Rotas;

public class MelhorCaminho {
    private String nome;
    private Rotas rotas;


    public String getNome() {
        return nome;
    }

    public void setNome(String nome) {
        this.nome = nome;
    }

    public Rotas getRotas() {
        return rotas;
    }

    public void setRotas(Rotas rotas) {
        this.rotas = rotas;
    }
}
