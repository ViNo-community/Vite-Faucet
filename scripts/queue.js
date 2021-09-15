module.exports = class ActionQueue {
    constructor(){
        this.actionQueues = new Map()
    }

    async queueAction(key, nextStep){
        if(!this.actionQueues.has(key)){
            this.actionQueues.set(key, {
                processing: false,
                queue: []
            })
        }
        const acc = this.actionQueues.get(key)
        acc.queue.push(()=>nextStep().then(resolve, reject))
        let resolve
        let reject
        
        return new Promise(async (r, j) => {
            resolve = r
            reject = j

            if(acc.processing)return
            acc.processing = true
            while(acc.queue[0]){
                const action = acc.queue.shift()
                await action()
            }
            this.actionQueues.delete(key)
        })
    }
}