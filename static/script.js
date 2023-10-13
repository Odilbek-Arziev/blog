const body = document.querySelectorAll(".message-body");

for (let message of body) {
    message.addEventListener("mouseover", () => {
        message.querySelector(".display").classList.remove("none");
    });

    message.addEventListener("mouseout", () => {
        message.querySelector(".display").classList.add("none");
    });
}

function toggleReply(pk){
    const replyContainer = document.querySelector(`.reply-${pk}`)
    replyContainer.classList.toggle('hidden')
}