package school.sptech.menor_tempo_atendimento.domain;

public class Rotas {
    private String modo;
    private Double tempoEstimado;


    public String getModo() {
        return modo;
    }

    public void setModo(String modo) {
        this.modo = modo;
    }

    public Double getTempoEstimado() {
        return tempoEstimado;
    }

    public void setTempoEstimado(Double tempoEstimado) {
        this.tempoEstimado = tempoEstimado;
    }
}
