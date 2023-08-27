import Component from '%jellyserve.component.not-compiled%';

const app = new Component({
    target: document.body,
    props: {
        data: "%jellyserve.component.data%"
    }
});

export default app;