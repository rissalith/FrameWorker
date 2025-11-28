/**
 * 精灵图动画播放器
 * 用于播放登录页背景的精灵图动画
 */

class SpriteAnimationPlayer {
    constructor() {
        // 三组精灵图动画配置 - 网格布局
        this.animations = [
            {
                name: '待机-张望',
                spritePath: '/images/待机-张望.webp',
                totalFrames: 122, // 总帧数
                columns: 10, // 10列
                rows: 13, // 13行(最后一行只有2帧)
                fps: 24, // 每秒24帧
                spriteImage: null, // 精灵图对象
                frameWidth: 0, // 单帧宽度
                frameHeight: 0, // 单帧高度
                loaded: false
            },
            {
                name: '待机-常态',
                spritePath: '/images/待机-常态.webp',
                totalFrames: 122,
                columns: 10,
                rows: 13,
                fps: 24,
                spriteImage: null,
                frameWidth: 0,
                frameHeight: 0,
                loaded: false
            },
            {
                name: '待机-深呼吸',
                spritePath: '/images/待机-深呼吸.webp',
                totalFrames: 122,
                columns: 10,
                rows: 13, // 10列×13行,共122帧
                fps: 24,
                spriteImage: null,
                frameWidth: 0,
                frameHeight: 0,
                loaded: false
            }
        ];

        this.currentAnimationIndex = 0;
        this.currentFrameIndex = 0;
        this.isPlaying = false;
        this.animationInterval = null;
        this.canvas = null;
        this.ctx = null;
        this.opacity = 0; // 用于淡入效果
        this.fadeInDuration = 1000; // 淡入持续时间(毫秒)
        this.fadeInStartTime = null;
    }

    /**
     * 初始化Canvas
     */
    init() {
        // 创建canvas元素
        this.canvas = document.createElement('canvas');
        this.canvas.id = 'sprite-animation-canvas';
        this.canvas.style.cssText = `
            position: absolute;
            top: -16%;
            left: 17%;
            width: 50%;
            height: 100%;
            object-fit: contain;
            object-position: left center;
            z-index: 1;
            pointer-events: none;
        `;
        
        // 插入到body的第一个子元素
        document.body.insertBefore(this.canvas, document.body.firstChild);
        
        this.ctx = this.canvas.getContext('2d');
        
        // 设置canvas尺寸
        this.resizeCanvas();
        window.addEventListener('resize', () => this.resizeCanvas());
        
        console.log('精灵图动画播放器已初始化 🎬');
        
        // 随机选择一个动画开始
        this.currentAnimationIndex = Math.floor(Math.random() * this.animations.length);
        
        // 加载当前精灵图
        this.loadSpriteSheet(this.currentAnimationIndex).then(() => {
            console.log('✅ 精灵图加载完成,开始播放');
            this.fadeInStartTime = Date.now();
            this.play();
            
            // 后台加载其他精灵图
            this.loadOtherSpriteSheets();
        });
    }

    /**
     * 调整Canvas尺寸
     */
    resizeCanvas() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }

    /**
     * 加载精灵图
     */
    async loadSpriteSheet(animationIndex) {
        const animation = this.animations[animationIndex];
        console.log(`⚡ 加载精灵图: ${animation.name}`);
        
        return new Promise((resolve, reject) => {
            const img = new Image();
            
            img.onload = () => {
                animation.spriteImage = img;
                // 网格布局,计算单帧尺寸
                animation.frameWidth = img.width / animation.columns;
                animation.frameHeight = img.height / animation.rows;
                animation.loaded = true;
                
                console.log(`✅ 精灵图 ${animation.name} 加载完成`);
                console.log(`   尺寸: ${img.width}x${img.height}`);
                console.log(`   网格: ${animation.columns}列 × ${animation.rows}行`);
                console.log(`   单帧: ${animation.frameWidth}x${animation.frameHeight}`);
                resolve();
            };
            
            img.onerror = () => {
                console.error(`❌ 加载失败: ${animation.spritePath}`);
                reject();
            };
            
            img.src = animation.spritePath;
        });
    }

    /**
     * 后台加载其他精灵图
     */
    async loadOtherSpriteSheets() {
        console.log('🔄 后台加载其他精灵图...');
        
        for (let i = 0; i < this.animations.length; i++) {
            if (i === this.currentAnimationIndex) continue;
            
            try {
                await this.loadSpriteSheet(i);
            } catch (error) {
                console.error(`加载精灵图 ${this.animations[i].name} 失败`);
            }
        }
        
        console.log('✅ 所有精灵图加载完成');
    }

    /**
     * 播放动画
     */
    play() {
        if (this.isPlaying) return;
        
        this.isPlaying = true;
        const animation = this.animations[this.currentAnimationIndex];
        const frameDelay = 1000 / animation.fps;
        
        console.log(`▶️ 播放精灵图动画: ${animation.name}`);
        
        this.animationInterval = setInterval(() => {
            this.renderFrame();
            this.currentFrameIndex++;
            
            // 当前动画播放完毕
            if (this.currentFrameIndex >= animation.totalFrames) {
                console.log(`✅ 动画 [${animation.name}] 播放完成，准备切换...`);
                this.currentFrameIndex = 0;
                
                // 切换到下一个动画
                this.switchToNextAnimation();
            }
        }, frameDelay);
    }

    /**
     * 渲染当前帧(从精灵图中提取)
     */
    renderFrame() {
        const animation = this.animations[this.currentAnimationIndex];
        
        if (!animation.loaded || !animation.spriteImage) {
            return;
        }
        
        // 计算淡入透明度
        if (this.fadeInStartTime) {
            const elapsed = Date.now() - this.fadeInStartTime;
            this.opacity = Math.min(1, elapsed / this.fadeInDuration);
            
            // 淡入完成后清除开始时间
            if (this.opacity >= 1) {
                this.fadeInStartTime = null;
            }
        }
        
        // 清空画布
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // 设置全局透明度
        this.ctx.globalAlpha = this.opacity;
        
        // 计算当前帧在精灵图中的位置(网格布局)
        // 网格布局：10列×13行
        const col = this.currentFrameIndex % animation.columns;
        const row = Math.floor(this.currentFrameIndex / animation.columns);
        const sourceX = col * animation.frameWidth;
        const sourceY = row * animation.frameHeight;
        const sourceWidth = animation.frameWidth;
        const sourceHeight = animation.frameHeight;
        
        // 添加调试日志（每30帧输出一次）
        if (this.currentFrameIndex % 30 === 0) {
            console.log(`🎬 [${animation.name}] 帧${this.currentFrameIndex}: 列${col}, 行${row}, 位置(${sourceX}, ${sourceY}), 透明度${this.opacity.toFixed(2)}`);
        }
        
        // 计算缩放，保持宽高比，适应canvas高度
        const scale = this.canvas.height / animation.frameHeight;
        const scaledWidth = animation.frameWidth * scale;
        const scaledHeight = animation.frameHeight * scale;
        
        // 居中显示
        const destX = (this.canvas.width - scaledWidth) / 2;
        const destY = 0;
        
        // 从精灵图中提取当前帧并绘制
        this.ctx.drawImage(
            animation.spriteImage,
            sourceX, sourceY, sourceWidth, sourceHeight, // 源矩形
            destX, destY, scaledWidth, scaledHeight // 目标矩形
        );
        
        // 恢复透明度
        this.ctx.globalAlpha = 1;
    }

    /**
     * 切换到下一个动画
     */
    async switchToNextAnimation() {
        const currentName = this.animations[this.currentAnimationIndex].name;
        
        // 停止当前播放
        this.stop();
        
        // 随机选择下一个动画（不重复当前）
        const nextIndex = (this.currentAnimationIndex + 1 + Math.floor(Math.random() * (this.animations.length - 1))) % this.animations.length;
        this.currentAnimationIndex = nextIndex;
        this.currentFrameIndex = 0;
        
        // 重置淡入效果
        this.opacity = 0;
        this.fadeInStartTime = Date.now();
        
        const nextAnimation = this.animations[nextIndex];
        
        console.log(`🔄 动画切换: [${currentName}] → [${nextAnimation.name}] (索引: ${this.currentAnimationIndex})`);
        
        // 如果下一个动画还没加载,先加载
        if (!nextAnimation.loaded) {
            console.log(`⏳ 加载下一个动画: ${nextAnimation.name}`);
            await this.loadSpriteSheet(nextIndex);
        }
        
        // 继续播放
        this.play();
    }

    /**
     * 停止播放
     */
    stop() {
        if (this.animationInterval) {
            clearInterval(this.animationInterval);
            this.animationInterval = null;
        }
        this.isPlaying = false;
    }

    /**
     * 销毁播放器
     */
    destroy() {
        this.stop();
        if (this.canvas && this.canvas.parentNode) {
            this.canvas.parentNode.removeChild(this.canvas);
        }
        // 清理精灵图引用
        this.animations.forEach(anim => {
            if (anim.spriteImage) {
                anim.spriteImage = null;
            }
        });
        window.removeEventListener('resize', () => this.resizeCanvas());
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    const player = new SpriteAnimationPlayer();
    player.init();
    
    // 将播放器实例挂载到window，方便调试
    window.spriteAnimationPlayer = player;
});